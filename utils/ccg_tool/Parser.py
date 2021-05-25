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

import copy
import logging

from spacy.lang.en import English
from spacy.tokenizer import Tokenizer
import torch.nn as nn
from nltk.ccg import chart, lexicon
import nltk

from dictionary import STRING2PREDICATE, WORD2NUMBER, RAW_LEXICON, LEXICON_HEAD
from constant import MAX_PHRASE_LEN, BEAM_WIDTH, SPECIAL_CHARS, REVERSE_SPECIAL_CHARS
#from ccg_rule_set import CustomRuleSet


nlp = English()
tokenizer = Tokenizer(nlp.vocab)

logger = logging.getLogger(__name__)


def is_quote_word(token):
    return (token.startswith("\'") and token.endswith("\'")) \
        or (token.startswith("\"") and token.endswith("\""))


def fill_whitespace_in_quote(sentence):
    """input: a string containing multiple sentences;
    output: fill all whitespaces in a quotation mark into underscore"""

    def convert_special_chars(s, flag):
        return SPECIAL_CHARS[s] if s in SPECIAL_CHARS and flag else s

    flag = False  # whether space should be turned into underscore, currently
    output_sentence = ''
    for i, s in enumerate(sentence):
        # deal with the special case "'s" of possession.
        is_not_posses = (i >= (len(sentence) - 2) or sentence[i:i+3] != '\'s ')
        if s in ("\"", "\'") and is_not_posses:
            # flip the flag if a quote mark appears
            flag = not flag
        output_sentence += convert_special_chars(s, flag)
    return output_sentence


def preprocess_sent(sentence):
    """input: a string containing multiple sentences;
    output: a list of tokenized sentences;
    originally designed to deal with _multiple_ sentences;
    code is modified here to deal with _one_ sentence."""
    sentence = fill_whitespace_in_quote(sentence)
    output = tokenizer(sentence)
    tokens = [x.text for x in output]

    # quick fix for ','
    new_tokens = []
    for _, token in enumerate(tokens):
        if token.endswith(','):
            new_tokens += [token.rstrip(','), ',']
        else:
            new_tokens += [token]
    return new_tokens


def string_to_predicate(s):
    """input: one string (can contain multiple tokens with ;
    output: a list of predicates."""
    if s != ',' and s not in REVERSE_SPECIAL_CHARS:
        s = s.lower().strip(',')
    if s.startswith("$"):
        return [s]
    if is_quote_word(s):
        temp_s = s[1:-1]
        if temp_s in STRING2PREDICATE:
            # upon request by Jane, if the quoted phrase exists in the dictionary,
            # we use the lexicon in the dictionary instead of treating it as a quoted noun phrase.
            return STRING2PREDICATE[temp_s]
        return [f"'{temp_s}'"]
    if s in STRING2PREDICATE:
        return STRING2PREDICATE[s]
    if s.isdigit():
        return [f"'{s}'"]
    if s in WORD2NUMBER:
        return [f"'{WORD2NUMBER[s]}'"]
    return []


def tokenize(sentence):
    """input: a list of tokens;
    output: a list of possible tokenization of the sentence;
    each token can be mapped to multiple predicates"""
    # log[j] is a list containing temporary results using 0..(j-1) tokens
    log = {i: [] for i in range(len(sentence) + 1)}
    log[0] = [[]]
    for i, token in enumerate(sentence):
        if not log[i] and i > 0: # fix to skip words not in the dictionary.
            log[i] = copy.copy(log[i-1])
        for _range in range(1, MAX_PHRASE_LEN + 1):
            if i + _range > len(sentence):
                break
            phrase = ' '.join(sentence[i:i + _range])
            predicates = string_to_predicate(phrase)
            for temp_result in log[i]:
                for predicate in predicates:
                    log[i + _range].append(temp_result + [predicate])
            if token.startswith("\"") or token.startswith("\'"):
                # avoid --"A" and "B"-- treated as one predicate
                break
    return log[len(sentence)]


def get_word_name(layer, st, idx):
    return "$Layer{}_St{}_{}".format(str(layer), str(st), str(idx))


def get_entry(word_name, category, semantics):
    return "\n\t\t{0} => {1} {{{2}}}".format(word_name, str(category), str(semantics))


def quote_word_lexicon(sentence):
    ret = ""
    for token in sentence:
        if is_quote_word(token):
            ret += get_entry(token, 'NP', token)
            ret += get_entry(token, 'N', token)
    return ret


class Parser(nn.Module):
    def __init__(self):
        super(Parser, self).__init__()
        self.raw_lexicon = RAW_LEXICON
        self.beam_width = BEAM_WIDTH

    def parse(self, sentence):
        """
        :param sentence: a list of tokens in one sentence.
                e.g. ['"may_be"', '$Is', '$Between', '$ArgX', '$And', '$ArgY']
        :return: a list of successful parses.
        """
        beam_lexicon = copy.deepcopy(self.raw_lexicon) + quote_word_lexicon(sentence)
        lexicon_used, children = {}, {}

        # the first index of forms is layer
        # the second index of forms is starting index
        all_forms = [[[token] for token in sentence]]

        # parsed results to be returned
        ret = []

        try:
            # Width of tokens to be parsed. Start with width 1 and stack to len(sentence)
            for layer in range(1, len(sentence)):
                layer_form = []

                # update the lexicon from previous layers
                lex = lexicon.fromstring(beam_lexicon, True)
                #parser = chart.CCGChartParser(lex, CustomRuleSet)
                parser = chart.CCGChartParser(lex, chart.DefaultRuleSet)

                # parse the span (st, st+layer)
                for st in range(0, len(sentence) - layer):
                    form = []
                    memory = []  # keep a memory and remove redundant parses
                    word_index = 0
                    ed = st + layer
                    # try to combine (st, split), (split+1, ed) into (st, ed)
                    for split in range(st, ed):
                        # get candidates for (st, split) and (split+1, ed)
                        words_L = all_forms[split-st][st]
                        words_R = all_forms[ed-split-1][split+1]
                        for word_L in words_L:
                            for word_R in words_R:
                                # try to combine word_L and word_R
                                try:
                                    for parse in parser.parse([word_L, word_R]):
                                        token, _ = parse.label()
                                        category, semantics = token.categ(), token.semantics()
                                        memory_key = str(category) + '_' + str(semantics)
                                        if memory_key not in memory:
                                            memory.append(memory_key)
                                            word_index += 1
                                            form.append((parse, category, semantics, word_index))
                                            word_name = get_word_name(layer, st, word_index)
                                            self.update_logs(parse, word_name, lexicon_used, children)
                                except (AssertionError, SyntaxError) as e:
                                    logger.info('Error when parsing %s and %s', word_L, word_R)
                                    logger.info('Error information: %s', e.args)
                    to_add = []
                    for item in form:
                        parse, category, semantics, word_index = item
                        word_name = get_word_name(layer, st, word_index)
                        to_add.append(word_name)
                        entry = get_entry(word_name, category, semantics)
                        if self.valid_entry(LEXICON_HEAD + entry):
                            beam_lexicon += entry
                        # if this is the last layer (covering the whole sentence)
                        # add this to output
                        if layer == len(sentence) - 1:
                            ret.append(str(semantics))
                    layer_form.append(to_add)
                all_forms.append(layer_form)
            # filter incomplete parses
            ret = list(filter(lambda x: x.startswith("'@"), ret))
        except Exception as e:
            return [], [], {}, {}, e
        # ret = sorted(ret, key=lambda x: self.forward_single(x), reverse=True)
        return ret, all_forms[-1][0], lexicon_used, children, None

    def update_logs(self, parse, word_name, lexicon_dict, children_dict):
        word_0_lex = parse[0].label()[0]
        word_1_lex = parse[1].label()[0]
        tokens_used = []
        children0 = [(word_name, (word_0_lex._token, word_1_lex._token))]
        if '$Layer' in word_0_lex._token:  # a compositional name
            tokens_used += lexicon_dict[word_0_lex._token]
            children0 += children_dict[word_0_lex._token]
        else:
            new_token = str(word_0_lex._token) + '|' + str(word_0_lex._categ) + '|{' + str(word_0_lex._semantics) + '}'
            tokens_used += [new_token]
        if '$Layer' in word_1_lex._token:  # a compositional name
            tokens_used += lexicon_dict[word_1_lex._token]
            children0 += children_dict[word_1_lex._token]
        else:
            new_token = str(word_1_lex._token) + '|' + str(word_1_lex._categ) + '|{' + str(word_1_lex._semantics) + '}'
            tokens_used += [new_token]
        lexicon_dict[word_name] = tokens_used
        children_dict[word_name] = children0

    def valid_entry(self, entry):
        """check if entry is valid."""
        valid = True
        try:
            _temp_lex = lexicon.fromstring(entry, True)
        except (AttributeError, nltk.sem.logic.LogicalExpressionException):
            valid = False
        return valid
