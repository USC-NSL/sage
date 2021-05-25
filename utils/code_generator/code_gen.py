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
import json
import pathlib
import sys

from termcolor import colored

UTILS_DIR = pathlib.Path(__file__).parent.absolute() / '..'
sys.path.insert(0, str(UTILS_DIR))
import connect_metadata_system as mds
import ops
import settings


def get_ops() -> dict:
    """ Get predicate operands. """
    return ops.OPS


def get_conversions(env: dict) -> dict:
    """ Get conversions table. Replace parameters according to
    environment.

    Parameter:
    env (dict): environment to aid logic form processing

    Returns:
    a conversion table (dict) in which the parameter placeholders are
    replaced according to values of env

    """
    def __replace_env_elements(element: str, env: dict) -> str:
        retval = element
        for key, value in env.items():
            retval = retval.replace(f'{{ENV_{key}}}', value)
            if key == 'message':
                retval = retval.replace(' ', '_')
        return retval

    conversions = {key: __replace_env_elements(value, env)
                   for key, value in settings.TERM_CONVERSIONS.items()}
    return conversions


def get_role(logic_form: str, role_conversions: dict) -> str:
    """ Get role(s) from keywords in logic form. """
    roles = []
    for keyword, role in role_conversions.items():
        if keyword in logic_form:
            roles.append(role)
    return ','.join(roles)


def parse_logic_form(logic_form: str) -> list:
    """ Parse logic_form to tokens

    Parameter:
    logic_form (str): logic form

    Returns:
    tokenized_logic_form (list): tokenized logic form

    """
    preproc_logic_form = (logic_form
                          .replace('(', ' ')
                          .replace("[dot]", ".")
                          .replace('[', '')
                          .replace(']', '')
                          .replace('"', '')
                          .replace('\'@', '(\'@')
                          .replace('(', ' ( ')
                          .replace(')', ' ) ')
                          .replace(',', ' '))
    tokens = preproc_logic_form.split()

    def __tokenize(tokens: list) -> list:
        """ Convert tokens to an expression.

        Inspired by https://norvig.com/lispy.html

        """
        if not tokens:
            raise SyntaxError("Invalid Logical Form")
        token = tokens.pop(0)
        if token == '(':
            lf_tokens = []
            while tokens[0] != ')':
                lf_tokens.append(__tokenize(tokens))
            tokens.pop(0)
            return lf_tokens
        if token == ')':
            raise SyntaxError("Invalid Logical Form")
        return token

    tokenized_logic_form = []
    while tokens:
        tokenized_logic_form.append(__tokenize(tokens))

    return tokenized_logic_form


def filter_logic_form(lf: list, denylist: list) -> bool:
    """ Checks whether logic form contains denylisted terms.

    Parameter:
    lf (list): logic form
    denylist (list): denylisted terms

    Returns:
    False if logic form contains denylisted term(s).
    True otherwise

    """
    keep_flags = []
    for term in lf:
        if isinstance(term, list):
            keep_flags.append(filter_logic_form(term, denylist))
        if isinstance(term, str):
            if term in denylist:
                keep_flags.append(False)
            else:
                keep_flags.append(True)
    return all(keep_flags)


def filter_logic_forms(lfs: list, denylist: list) -> list:
    """ Remove logic forms that has denylisted terms. """
    return [lf for lf in lfs if filter_logic_form(lf, denylist)]


def __process_content(content: str, conversions: dict) ->  str:
    """ Replace chunks in content.

    Parameter:
    content (str): text to process
    conversions (dict): conversion table

    Returns:
    ret (str): copy of content with replaced parts

    """
    ret = content
    for old, new in conversions.items():
        ret = ret.replace(old, new)
    return ret


def prepreprocess_logic_form(lfs: str, conversions: dict) -> str:
    """ Replace chunks of logic forms. """
    return __process_content(lfs, conversions)


def preprocess_logic_form(lf, conversions: dict) -> list:
    """ Preprocess a single logic form. """
    new_lf = []
    for term in lf:
        if isinstance(term, list):
            term = preprocess_logic_form(term, conversions)
        elif isinstance(term, str):
            if conversions.get(term):
                term = conversions[term]
        new_lf.append(term)
    return new_lf


def preprocess_logic_forms(lfs: list, conversions: dict) -> list:
    """ Preprocess a consecutive logic forms. """
    return [preprocess_logic_form(logic_form, conversions)
            for logic_form in lfs]


def eval_logic_forms(lfs: list, env=None) -> list:
    """ Evaluate consecutive logic forms. """
    if env is None:
        env = {}
    return [eval_logic_form(lf, env) for lf in lfs]


def eval_logic_form(lf, env=None):
    """ Evaluate a single logic form. """
    if env is None:
        env = {}
    if not isinstance(lf, list):
        return lf
    func, *params = lf
    if not isinstance(func, str):
        eval_logic_form(func, env)
    params = [eval_logic_form(param, env) for param in params]
    return get_ops()[func](params, env)


def postprocess_code(code: str, conversions: dict) -> str:
    """ Replace chunks of code. """
    processed = __process_content(code, conversions)
    # remove trailing ';' from @Comment
    if processed.startswith('//'):
        processed = processed.replace(';', '')
    return processed


def write_code_to_file(code: str, file_name: str, mode='a'):
    """ Write generated code to a file. """
    with open(file_name, mode) as out_file:
        out_file.write(code)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument(
        'logicform',
        help='Logic form to process',
        type=str,
    )
    parser.add_argument(
        '--sentence',
        help='Sentence (set if you use --mds)',
        type=str,
    )
    parser.add_argument(
        '--sentence_id',
        help='Sentence ID (set if you use --mds)',
        type=int,
    )
    parser.add_argument(
        '--use_metadata_system', '-mds',
        help='Use MetadataSystem to get environment information',
        action='store_true',
    )
    parser.add_argument(
        '--env', '-e',
        help='Environment to aid logic form processing',
        type=str,
        default='',
    )
    parser.add_argument(
        '--quiet', '-q',
        help='Surpress verbose mode',
        action='store_true',
    )
    parser.add_argument(
        '--outfile', '-o',
        help='Write generated code to this file',
        type=str,
        default='',
    )
    parser.add_argument(
        '--outfile_mode',
        help='Open mode for output file: w (write), a (append)',
        type=str,
        choices=['w', 'a'],
        default='a',
    )
    args = parser.parse_args()

    env_arg = json.loads(args.env)
    sentence = ""
    if args.use_metadata_system:
        try:
            sentence = args.sentence.strip()
        except AttributeError:
            print(colored("Error: --sentence is missing", "yellow"))
        try:
            env_arg.update(mds.get_env_from_mds(env_arg['message'],
                                                env_arg['field'],
                                                args.logicform,
                                                sentence,
                                                args.sentence_id))

        except (json.JSONDecodeError, StopIteration, LookupError) as error:
            print(colored('Error during querying MDS info for logic form: '
                          f'"{args.logicform}"\t{error}',
                          'red'))
    if args.env:
        env_arg.update(json.loads(args.env))
    if not 'role' in env_arg:
        env_arg.update({'role': get_role(args.logicform,
                                         settings.ROLE_KEYWORDS)})

    prepreprocessed_lf = prepreprocess_logic_form(args.logicform,
                                                  settings.LF_CONVERSIONS)
    tokenized_lfs = parse_logic_form(prepreprocessed_lf)
    filtered_lfs = filter_logic_forms(tokenized_lfs,
                                      settings.DENYLIST)
    preprocessed_lfs = preprocess_logic_forms(filtered_lfs,
                                              get_conversions(env_arg))
    eval_res = eval_logic_forms(preprocessed_lfs, env_arg)
    res = postprocess_code("{};\n".format(';\n'.join(eval_res)),
                           settings.CODE_CONVERSIONS)

    if not args.quiet:
        print(f'    LF: {args.logicform}\n'
              f'   ENV: {env_arg}\n'
              f'RESULT: {res}')

    if args.use_metadata_system:
        try:
            sent_rec = mds.get_sentence_row(env_arg['message'],
                                            env_arg['field'],
                                            args.logicform,
                                            sentence,
                                            args.sentence_id)
            mds.register_code_env(sent_rec, res, env_arg)
        except Exception as error:
            print(colored(f'Error registering env and code to MDS: {error}',
                          'red'))

    if args.outfile:
        write_code_to_file(res, args.outfile, args.outfile_mode)
