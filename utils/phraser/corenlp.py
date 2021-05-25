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
import os
import pathlib
import subprocess
import sys

from trial import run_spacy
from term import TermDB
from coref import coref_resol

CUR_DIR = pathlib.Path(__file__).parent.absolute()
MDS_DIR = CUR_DIR / '..' / 'metadata_system'
sys.path.insert(0, str(MDS_DIR))
import sentence_record


def get_argparse():
    arg_parser = argparse.ArgumentParser()
    arg_parser.add_argument(
        '--sentence', '-s',
        help='sentence',
        type=str,
    )
    arg_parser.add_argument(
        '--sentence_id', '-i',
        help='sentence id',
        type=int, default=-1,
    )
    arg_parser.add_argument(
        '--path', '-p',
        help='specify the write_in filename for AutoPhrase label',
        type=str, default='data/EN/input.txt',
    )
    arg_parser.add_argument(
        '--enable_ap', '-e',
        help='enable autophrase label',
        action='store_true',
    )
    arg_parser.add_argument(
        '--debug', '-d',
        help='Print debug messages',
        action='store_true',
    )
    return arg_parser


def remove_stopword(lists):
    stopwords = ("a", "an", "the")
    new_ls = []
    for sentence in lists:
        sentence_words = sentence.split()
        resultwords = [word for word in sentence_words if word.lower() not in stopwords]
        sentence = ' '.join(resultwords)
        new_ls.append(sentence)
    return new_ls


def spacy_extract(target_str):
    spacy_result = run_spacy(target_str)
    result = remove_stopword(spacy_result)
    return result


def trim_tail(sentence):
    ending_chars = (",", ".", ";")
    if sentence[-1] in ending_chars:
        return sentence[:-1]
    return sentence


def term_dict_label(target_string):
    term_db = TermDB()
    target_split = target_string.split()
    str_lower = target_string.lower()
    str_split = str_lower.split()
    index = 0
    term_ls = []
    term_len = []
    term_index = []
    ending_chars = (",", ".", ";")
    for i, token in enumerate(str_split):
        if i == 0 or i >= index:
            find = term_db.get_term_by_first_word(token)
            if find:
                np_ls = [entry[1] for entry in find]
                match = False
                match_len = 0
                for np in np_ls:
                    sub_sent = ' '.join(str_split[i:i+len(np.split())])
                    if np in sub_sent:
                        match = True
                        if len(np) > match_len:
                            match_len = len(np.split())
                if match:
                    term_index.append(i)
                    term_len.append(match_len)
                    index += match_len
    for j, index in enumerate(term_index):
        slice_end_idx = index + term_len[j]
        term_ls.append(" ".join(target_split[index:slice_end_idx]))
    for k, term in enumerate(term_ls):
        if term[-1] in ending_chars:
            term_ls[k] = term_ls[k][:-1]
    return term_ls


def quote_words(sentence):
    ending_chars = [",", ".", ";"]
    sent_split = sentence.split()
    find_start = False
    start_index = []
    end_index = []
    # print(sent_split)
    for i, token in enumerate(sent_split):
        if "NP" in token and not find_start:
            find_start = True
            start_index.append(i)
            if token[-1] in ending_chars:
                find_start = False
                end_index.append(i)
        elif "NP" in token and token[-1] in ending_chars:
            find_start = False
            end_index.append(i)
        elif "NP" not in token and find_start:
            find_start = False
            end_index.append(i-1)
    if find_start:
        end_index.append(-1)
    for index in start_index:
        replace_word = f"'{sent_split[index]}"
        sent_split[index] = replace_word
    for index in end_index:
        if sent_split[index][-1] in ending_chars:
            sent_split[index] = f"{sent_split[index][:-1]}'{sent_split[index][-1]}"
        else:
            replace_word = f"{sent_split[index]}'"
            sent_split[index] = replace_word
    new_sent = ' '.join(sent_split)
    return new_sent


if __name__ == "__main__":
    argparser = get_argparse()
    args = argparser.parse_args()
    sent = args.sentence
    sent_orig = args.sentence
    sent_id = args.sentence_id
    file_path = CUR_DIR / args.path
    output_file = CUR_DIR / 'models' / 'DBLP' / 'output.txt'
    if not os.path.exists(output_file):
        os.makedirs(os.path.dirname(output_file), exist_ok=True)

    sent = trim_tail(sent)

    ### Run dictionary mapping ###
    nps_term_dic = term_dict_label(sent)
    term_map = {np: f'NP_TERM{index}' for index, np in enumerate(nps_term_dic)}
    for key in sorted(term_map, key=len, reverse=True):
        sent = sent.replace(key, term_map[key])
    if args.debug:
        print('sent:', sent)

    ### Run SpaCy ###
    nps_spacy = spacy_extract(sent)
    if args.debug:
        print("SpaCy label:", nps_spacy)

    mapping_dict = {np: f'NP{index}' for index, np in enumerate(nps_spacy)}
    if args.debug:
        print('mapping_dict:', mapping_dict)

    for key in sorted(mapping_dict, key=len, reverse=True):
        sent = sent.replace(key, mapping_dict[key])

    if args.debug:
        print('sent:', sent)

    ### Run AutoPhrase ###
    if args.enable_ap:
        with open(file_path, 'w') as f:
            f.write(sent)
        # do the segmentation
        subprocess.call([str(CUR_DIR / 'phrasal_segmentation.sh')])
        # use the result
        with open(output_file, 'r') as ap_outfile:
            new_sent = ap_outfile.read()
        if args.debug:
            print('new_sent:', new_sent)
    else:
        new_sent = sent

    new_sent = quote_words(new_sent)
    if args.debug:
        print("quote: \n", new_sent)

    mapping_dict = {value: key for key, value in mapping_dict.items()}
    if args.debug:
        print(mapping_dict)
    for key in mapping_dict:
        replace_word = f"{mapping_dict[key]}"
        if args.debug:
            print('mapping_dict', key, ' ', replace_word)
        new_sent = new_sent.replace(key, replace_word)
    if args.debug:
        print(new_sent)

    term_map = {value: key for key, value in term_map.items()}
    for key in term_map:
        replace_word = f"{term_map[key]}"
        if args.debug:
            print('term_map', key, ' ', replace_word)
        new_sent = new_sent.replace(key, replace_word)


    ### Coreference Resolution ###
    new_sent = coref_resol(new_sent)
    print("NP labelled sentence with coreference resolution: \n\t", new_sent)

    sent_db = sentence_record.SentenceDB()
    sentence = sent_orig.lstrip(" ")
    label = (new_sent
             .lstrip(" ")
             .replace("</phrase>", "'")
             .replace("<phrase>", "'"))
    sent_record = sentence_record.SentenceRecord(sentence=sentence,
                                                 sent_id=sent_id,
                                                 label=label)
    sent_db.replace_value(sent_record)

    with open(output_file, 'w') as ap_outfile:
        ap_outfile.write(new_sent)
