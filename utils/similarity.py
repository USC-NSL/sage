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

#import os
#os.environ["SPACY_WARNING_IGNORE"] = "W008"

import difflib

import spacy


def diff_pick(first_ls: list, word: str) -> tuple:
    new_list = [difflib.SequenceMatcher(None, i, word).ratio() for i in first_ls]
    index = new_list.index(max(new_list))
    if new_list[index] > 0.5:
        return True, first_ls[index]
    return False, first_ls[index]

def similarity_lsmap(first_ls: list, second_ls: list) -> list:
    """
    Input: two lists
                 first_ls should be the db fields
                 second_ls should be the paragraph titles
    """
    nlp = spacy.load('en_core_web_md')
    matrix = []
    nlp_token1 = [nlp(elem) for elem in first_ls]
    nlp_token2 = [nlp(elem) for elem in second_ls]
    for elem2 in nlp_token2:
        row_ls = [elem2.similarity(elem1) for elem1 in nlp_token1]
        index = row_ls.index(max(row_ls))
        matrix.append((first_ls[index], row_ls[index]))
    print(matrix)
    return matrix


def similarity_map(first_ls: list, word: str) -> tuple:
    """
    Input: one string and one list
                 first_ls should be the db field
                 word is the string that needs to be matched
    """
    nlp = spacy.load('en_core_web_md')
    token = nlp(word)
    candidate = [token.similarity(nlp(elem)) for elem in first_ls]
    index = candidate.index(max(candidate))
    # print('index', str(index), 'similarity: ', candidate[index])
    good_match = False
    if candidate[index] > 0.5:
        print("Find candidate:", first_ls[index])
        good_match = True
    else:
        print('no good matching')
    return good_match, first_ls[index]


def similarity_select(ls: list, word_list: list) -> list:
    nlp = spacy.load('en_core_web_md')
    words = [word for word in word_list if nlp(word).has_vector]
    elems = [elem for elem in ls if nlp(elem).has_vector]
    failed = []
    for word in words:
        ever = False
        for elem in elems:
            token = nlp(word)
            compare = nlp(elem)
            if token and token.vector_norm and compare and compare.vector_norm:
                if token.similarity(compare) > 0.5:
                    ever = True
                    break
        if not ever:
            print(word)
            failed.append(word)
    print(failed)
    return failed

if __name__ == '__main__':
    similarity_map(['icmp_type', 'checksum'], 'checksum_field')
