#! /usr/bin/env python3

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
import pathlib
import sys

from tabulate import tabulate
from termcolor import colored

from Parser import Parser, preprocess_sent, tokenize, string_to_predicate, is_quote_word
from dictionary import RAW_LEXICON


CUR_DIR = pathlib.Path(__file__).parent.absolute()

LFC_DIR = CUR_DIR / '..' / 'logic_form_checker'
sys.path.insert(0, str(LFC_DIR))
import check_logic_forms as clf

MDS_DIR = CUR_DIR / '..' / 'metadata_system'
sys.path.insert(0, str(MDS_DIR))
import sentence_record



def rfc_lex_parse(cli_args: argparse.Namespace):
    """ All-in-one functon to parse and process a sentence

    Parameter:
    cli_args (argparse.Namespace): parsed CLI args
    """
    sent = cli_args.str
    new_sent = preprocess_sent(sent)
    sent_tokenized = tokenize(new_sent)
    if cli_args.debug:
        print(sent)
        print(new_sent)
        print(sent_tokenized)

    parser = Parser()
    results = []
    denylist = ('\\', 'None')

    for tokenized in sent_tokenized:
        parses, names, lex_dict, child_dict, bp_exception = parser.parse(tokenized)
        if cli_args.debug:
            print(parses)
        if bp_exception:
            print(f'beam_parse: {bp_exception.__class__}: {bp_exception}')
        for parse, name in zip(parses, names):
            if not any(s in parse for s in denylist):
                results.append(parse)
                if cli_args.debug:
                    format_dict = {'parse': parse,
                                   'name': name,
                                   'lex': lex_dict[name],
                                   'child': child_dict[name]}
                    print("{parse} --> \n\t{name}: {lex}\n{child}\n".format(**format_dict))

    num_results = len(results)
    if num_results == 0:
        return '', None
    ir_results = list(set(results))
    print(f"IR numbers: {len(ir_results)}")
    if cli_args.debug:
        print(ir_results)
    if num_results > 1:
        print(colored("multiple logical forms", 'red'))

    lf_graphs = []
    if cli_args.check and num_results > 1:
        print('Find equivalent logical forms:')
        lf_graphs = clf.check_all(ir_results, checks=cli_args.checks, verbose=True)
    else:
        lf_graphs = clf.convert_all(ir_results)

    print(colored('Final logical forms:', 'green'))
    clf.print_all(lf_graphs)

    # file/db IO
    if cli_args.wrtdot:
        clf.export_all(lf_graphs, out_dir='/tmp', out_format='pdf')
    if not cli_args.norecord:
        if cli_args.debug:
            print('Recording logical forms to metada system')
        record_logical_form_graphs(sent, lf_graphs, cli_args.env,
                                   cli_args.msg_type, cli_args.field_name)

    try:
        lf = lf_graphs[0]['graph'].logic_form
    except IndexError:
        lf = ''
    return lf, retrieve_sentence_and_id(sent)


def retrieve_sentence_and_id(label_sent: str) -> tuple:
    """ Retrieve sentence and id by labelled sentence
    Parameter:
    label_sent (str): labelled sentence
    """
    sentence_db = sentence_record.SentenceDB()
    mapping = sentence_db.get_mapping_by_label(label_sent)
    try:
        sentence = mapping[0][0]
        sentence_id = mapping[0][1]
    except IndexError:
        print('Failed to retrieve sentence and sentence_id')
        sentence = ''
        sentence_id = -1
    return (sentence, sentence_id)


def record_logical_form_graphs(label_sent: str, logical_form_graphs: list, env: str,
                               msg_type: str, field: str):
    """ Write logical forms and logical form graphs to metadata system.

    Parameter:
    label_sent (str): labelled sentence
    logical_form_graphs (list): dicts of id (int) and a graph (LogicalFormGraph)

    """
    label_sent = label_sent.lstrip(' ')
    sentence_db = sentence_record.SentenceDB()
    for lf_graph in logical_form_graphs:
        mapping = sentence_db.get_mapping_by_label(label_sent)
        try:
            sentence = mapping[0][0].lstrip(' ')
            sentence_id = mapping[0][1]
            msg = msg_type
            lf = lf_graph['graph'].logic_form
            sent_record = sentence_record.SentenceRecord(sentence=sentence,
                                                         sent_id=sentence_id,
                                                         msg_type=msg,
                                                         field=field,
                                                         label=label_sent,
                                                         lf=lf,
                                                         env=env)
            sentence_db.replace_value(sent_record)
            sentence_db.update_lf_graph(sent_record, lf_graph['graph'].graph)
        except IndexError:
            txt = (f'Error in recording logical form: '
                   f'no entry for label "{label_sent}".')
            print(txt)


def display_debug_information(cli_args: argparse.Namespace):
    """ Debug and analyze how a sentence is parsed

    Parameter:
    cli_args (argparse.Namespace): parsed CLI args
    """
    sent = cli_args.str
    new_sent = preprocess_sent(sent)
    print(f'Parsed sentence: {sent}')
    print(f'Split the sentence: {new_sent}')
    raw_lexicon = RAW_LEXICON.split("\n")
    raw_lexicon = [x.lstrip() for x in raw_lexicon]
    lexicon_mapping = {}
    for lexicon in raw_lexicon:
        try:
            lexicon_split = lexicon.split(" => ")
            pred, lex = lexicon_split[0], lexicon_split[1]
            if pred not in lexicon_mapping:
                lexicon_mapping[pred] = [lex]
            else:
                lexicon_mapping[pred].append(lex)
        except:
            continue
    result = []
    for token in new_sent:
        predicates = string_to_predicate(token)
        if not predicates:
            print('Bad token:')
            print(f'\t\"{token}\" has no predicate mapping')
            new_sent.remove(token)
        else:
            for predicate in predicates:
                if is_quote_word(predicate):
                    lexicon_mapping[predicate] = 'NP'
                mapped_lex = lexicon_mapping[predicate]
                for mapping in mapped_lex:
                    result.append([token, predicate, mapping])
    print('\n')
    print(tabulate(result, headers=["Token", "Predicate", "Lexicon"]))


if __name__ == "__main__":
    argparser = argparse.ArgumentParser()
    argparser.add_argument(
        '--str', '-s',
        help='Specify target filename',
        default="The 'checksum' is zero",
    )
    argparser.add_argument(
        '--check', '-c',
        help='Check equivalent logic forms',
        action="store_true",
    )
    argparser.add_argument(
        '--checks', '-C',
        help='Checks to execute',
        choices=clf.CHECKS,
        nargs='+',
    )
    argparser.add_argument(
        '--pushir', '-pi',
        help='Push IR to MDS for assign/associate',
        action="store_true",
    )
    argparser.add_argument(
        '--irstr', '-is',
        help='Pushed IR string (only one)',
        type=str,
        default='',
    )
    argparser.add_argument(
        '--norecord', '-nr',
        help='Do not store LF graphs in Metadata System',
        action="store_true",
    )
    argparser.add_argument(
        '--debug', '-d',
        help='Enable debug mode',
        action="store_true",
    )
    argparser.add_argument(
        '--wrtdot', '-w',
        help='Write logical form graphs to pdf to /tmp/lfg-*.',
        action="store_true",
    )
    argparser.add_argument(
        '--env', '-e',
        help='Environment to aid logic form processing',
        type=str,
        default='',
    )
    argparser.add_argument(
        '--msg_type', '-m',
        help='msg_type to aid register to MDS',
        default=''
    )
    argparser.add_argument(
        '--field_name', '-n',
        help='field to aid register to MDS',
        default=''
    )
    argparser.add_argument(
        '--display_debug', '-dd',
        help='Display debug message without filtering non-complete sentence parsing',
        action="store_true",
    )
    args = argparser.parse_args()

    if args.display_debug:
        display_debug_information(args)
    else:
        parsed, recv = rfc_lex_parse(args)
        if not None in (parsed, recv):
            send_back_data = f"{parsed}~{recv[0]}~{str(recv[1])}~"
            ccg_result_file = CUR_DIR / 'CCGresult.txt'
            with open(ccg_result_file, "w") as f:
                f.write(send_back_data)
