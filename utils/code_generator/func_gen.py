#!/usr/bin/env python3

# Copyright (c) 2021, The University of Southern California.
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#
# 1. Redistributions of source code must retain the above copyright notice,
# this list of conditions and the following disclaimer.
#
# 2. Redistributions in binary form must reproduce the above copyright notice,
# this list of conditions and the following disclaimer in the documentation
# and/or other materials provided with the distribution.
#
# 3. Neither the name of the copyright holder nor the names of its contributors
# may be used to endorse or promote products derived from this software without
# specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
# ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE
# LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR
# CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF
# SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS
# INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN
# CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE)
# ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
# POSSIBILITY OF SUCH DAMAGE.

import argparse
import collections
import re
import subprocess
import tempfile
from pathlib import Path

from termcolor import colored

import connect_metadata_system as mds
from code_gen import write_code_to_file, __process_content
import settings


class CodeSnippet:
    """ Store a code chunk with its environment and comment. """
    def __init__(self, env, code, comment=""):
        self.env = env
        self.code = code
        self.comment = comment

    def __repr__(self):
        ret = (f'ENV: {self.env}\n'
               f'CODE: {self.code}\n')
        if self.comment:
            ret = f'{ret}COMMENT: {self.comment}\n'
        return ret


def get_codesnippets_from_mds(message: str) -> list:
    """ Get code snippets of a given message type.

    Parameters:
    message (str): name of message type to query

    Returns:
    list of CodeSnippet objects which store code relevant to the
    message type sorted by occurance of the corresponding sentence in
    text

    """
    return [CodeSnippet(row['env'], row['code'].strip(),
                        comment=row['sentence'])
            for row in sorted(mds.get_message_envs_codes_sentences(message),
                              key=lambda r: r['sentence_id'])]


def filter_codesnippets(code_snippets: list, role: str) -> list:
    """ Keep code snippets relevant to implement a given role,
    filter duplicates.

    Parameters:
    code_snippets (list): list of CodeSnippet objects
    role (str): keep code snippets that has the given role or has no
    role at all

    Returns:
    list of CodeSnippets relevant to implement a given role

    """
    char_denylist = (';')
    filtered_snippets = []
    duplicates = set()
    for snippet in code_snippets:
        if snippet.code not in char_denylist:
            if snippet.code not in duplicates:
                if role in snippet.env['role'] or snippet.env['role'] == '':
                    filtered_snippets.append(snippet)
                    duplicates.add(snippet.code)
            else:
                first_snippet = next(cs for cs in filtered_snippets if
                                     cs.code == snippet.code)
                first_snippet.comment += "\n // {}".format(snippet.comment)
    return filtered_snippets


def get_associated_args(code_snippets: list) -> list:
    """ Collect associated function arguments.

    Parameters:
    code_snippets (list): list of CodeSnippet objects

    Returns:
    assoc_args (list): associated function arguments lexically sorted

    """
    code = "".join(s.code for s in code_snippets)
    fieldname_regex = r'(\w+) = (\1)_value;'
    assoc_args = {f'int {cap[1]}_value' for cap in
                  re.findall(fieldname_regex, code)}
    if 'ptrs->' in code:
        assoc_args.add('proto_ptr_t *ptrs')
    return sorted(assoc_args)


def sort_codesnippets(code_snippets: list, prio_rules: dict) -> list:
    """ Sort codesnippets according to field priority rules and advices. """
    # collect fields
    snippets = collections.defaultdict(list)
    for snippet in code_snippets:
        snippets[snippet.env['field']].append(snippet)
    # determine order
    order = list(snippets.keys())
    position = {0: 0, -1: len(order)}
    for field, prio in prio_rules:
        try:
            order.remove(field)
            order.insert(position[prio], field)
        except ValueError as error:
            print(colored(f'Error: "{field}" is not a valid field name',
                          'red'))
            raise error
    # rearrange snippets: 1) follow order, 2) bring advices front
    ret_val = [c for o in order
               for c in sorted(snippets[o],
                               key=lambda x: x.env.get('advice', False),
                               reverse=True)]
    return ret_val


def concat_codesnippets(code_snippets: list, with_comments=False) -> str:
    """ Concatenate code snippets to a single code block string. """
    if with_comments:
        snippets = map(lambda c: f'//{c.comment}\n{c.code}\n'
                       if c.comment and not c.code.startswith('//')
                       else c.code,
                       (c for c in code_snippets))
    else:
        snippets = (c.code for c in code_snippets)
    instructions = "\n".join(snippets)
    return instructions


def add_variable_declarations(message: str, code_snippets: list) -> list:
    """ Add variable declarations to the beginning of code snippets. """
    spec_fields = set()
    for fields in mds.get_msg_fields(message):
        name, size = fields[0], int(fields[1])
        if not 0 < size <= 64:
            spec_fields.add(name.replace(' ', '_').replace('+', 'w'))
    for offset, field in enumerate(spec_fields, start=1):
        field = __process_content(field.lower(), settings.CODE_CONVERSIONS)
        code = f'char *{field.lower()} = (char *) (hdr + {offset});'
        env = {'field': field, 'role': ''}
        code_snippets.insert(0, CodeSnippet(env, code))
        offset += 1
    return code_snippets


def get_function_name(proto: str, message: str, role: str, prefix='fill') -> str:
    """ Construct function name.

    Parameters:
    proto (str): corresponding protocol
    message (str): message type implemented in function
    role (str): role implemented in function
    prefix (str): add prefix to the beginning of the function name

    Returns:
    function name as string

    """
    try:
        msg = settings.MSG_ABBREVS[message]
    except KeyError:
        msg = message.replace(' Message', '').replace(' ', '_').lower()
    return f'{prefix}_{proto}_{msg}_{role}'


def create_function_def(return_type: str, function_name: str,
                        func_params: list) -> str:
    """ Create a function definition/header

    Parameters:
    return_type (str): type of function's return value
    function_name (str): name of the function
    func_params (list): storing argument type and name as string
    function parameters

    Returns:
    string of function definition w/o ending char

    """
    function_args = ", ".join(p for p in func_params if p)
    return f"{return_type} {function_name}({function_args})"


def create_function(code_snippets: list, func_line: str,
                    with_comments=False) -> str:
    """ Create a whole function code

    Parameters:
    code_snippets (list): list of CodeSnippet objects
    func_line (str): line to use as the beginning of the generated
    funciton
    with_comments (bool): add comments

    Returns:
    function (str): function code

    """
    instructions = concat_codesnippets(code_snippets, with_comments)
    function = '{} {{\n{}\n}}\n'.format(func_line, instructions)
    return function


def format_code(code: str, clang_args="") -> str:
    """ Format code using 'clang-format'.

    Parameters:
    code (str): generated code
    clang_args (str): CLI args for 'clang-format'

    Returns:
    code formatted by 'clang-format'

    """
    output = ""
    clang_config = "BasedOnStyle: Google\nSpaceAfterCStyleCast: true"
    with tempfile.TemporaryDirectory() as tmpdir:
        formatfile = open(Path(tmpdir, ".clang-format"), 'w+t')
        formatfile.write(clang_config)
        formatfile.close()
        tmpfile = open(Path(tmpdir, "code.cpp"), 'w+t')
        tmpfile.write(code)
        tmpfile.close()
        cmd = f'clang-format -style=file {clang_args} {tmpfile.name}'
        output = subprocess.check_output(cmd.split()).decode()
    return output


if __name__ == "__main__":
    argparser = argparse.ArgumentParser()
    argparser.add_argument(
        '--message', '-m',
        help='Message to generate',
        type=str,
    )
    argparser.add_argument(
        '--role', '-r',
        help='Role to use. Options: sender,receiver',
        type=str,
    )
    argparser.add_argument(
        '--comments', '-c',
        help='Generate comments',
        action='store_true',
    )
    argparser.add_argument(
        '--outfile', '-o',
        help='Write generated code to this file',
        type=str,
        default='',
    )
    argparser.add_argument(
        '--outfile_mode',
        help='Open mode for output file: w (write), a (append)',
        type=str,
        choices=['w', 'a'],
        default='a',
    )
    argparser.add_argument(
        '--quiet', '-q',
        help='Surpress verbose mode',
        action='store_true',
    )
    argparser.add_argument(
        '--special_purpose', '-sp',
        help='Catering to specific static framework',
        action='store_true',
    )
    args = argparser.parse_args()

    if not args.role:
        raise Exception('Please, set role with [--role/-r ROLE]')

    codesnippets = get_codesnippets_from_mds(args.message)
    filtered_codesnippets = filter_codesnippets(codesnippets, args.role)
    associated_args = get_associated_args(codesnippets)
    sorted_codesnippets = sort_codesnippets(filtered_codesnippets,
                                            settings.RANK_FIELDS[args.message])
    additional_args = ', '.join(associated_args)
    if args.special_purpose:
        func_args = (f'struct {args.message.replace(" ", "_")}_hdr *hdr',
                    'uint16_t length',
                     additional_args,
                    )
    else:
        func_args = (f'{args.message.replace(" ", "_")}_hdr *hdr',
                     'uint16_t length',
                     additional_args,
                     )
    protocol = codesnippets[0].env['protocol'].lower()
    func_name = get_function_name(protocol, args.message, args.role, 'fill')
    function_line = create_function_def('void', func_name, func_args)
    extended_snippets = add_variable_declarations(args.message,
                                                  sorted_codesnippets)
    function_code = create_function(extended_snippets, function_line,
                                    with_comments=args.comments)
    formatted_code = format_code(function_code)

    if not args.quiet:
        print(formatted_code)

    if args.outfile:
        write_code_to_file(formatted_code, args.outfile, args.outfile_mode)
