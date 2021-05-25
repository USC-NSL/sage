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
from collections import defaultdict

CUR_DIR = pathlib.Path(__file__).parent.absolute()
MDS_DIR = CUR_DIR / '..' / 'metadata_system'
sys.path.insert(0, str(MDS_DIR))
from metarecord import MetaRecord, MetaDB
from sentence_record import SentenceRecord, SentenceDB

LFC_DIR = CUR_DIR / '..' / 'logic_form_checker'
sys.path.insert(0, str(LFC_DIR))
import check_logic_forms as clf
import check_predicates as cp

TERM_DIR = CUR_DIR /'..' / 'phraser'
sys.path.insert(0, str(TERM_DIR))
import term as tm

SIM_DIR = CUR_DIR /'..'
sys.path.insert(0, str(SIM_DIR))
from similarity import similarity_select


def get_sentence_row(msg_type: str, field: str, lf: str,
                     sent: str, sent_id: int) -> SentenceRecord:
    """ Query a sentence record from the MetaData System. """
    db = SentenceDB()
    rows = db.get_mapping_by_msgtype_lf_and_sent_with_id(msg_type, field,
                                                         lf, sent, sent_id)
    db.close_conn()
    return SentenceRecord(*rows[0])


def get_all_lf(msg_type: str, proto='icmp'):
    """ Query all logical forms from the MetaData System. """
    sent_db = SentenceDB()
    sent_rows = sent_db.get_mapping_by_msg_type(msg_type)
    sent_db.close_conn()
    meta_db = MetaDB()
    meta_rows = meta_db.get_meta_by_msg_type(msg_type)
    meta_db.close_conn()
    fields = list(set(meta_row[3] for meta_row in meta_rows))
    add_list = [f'{proto} {field}' for field in fields]
    fields.extend(add_list)
    fields.append(msg_type)
    term_db = tm.TermDB()
    term_rows = term_db.get_all_term()
    term_db.close_conn()
    terms = [term_row[1] for term_row in term_rows]
    actions = ['help', 'aid', 'match', 'form', 'recompute', 'reverse', 'compute']
    numbers = ['zeros', 'one', 'two', 'three', 'eight']
    lfs = list(set((row[4] for row in sent_rows if row[4] != '')))
    lf_graphs = clf.convert_all(lfs)
    str_list = []
    for lf_graph in lf_graphs:
        graph_lf_graph = lf_graph['graph'].graph
        for node in graph_lf_graph.nodes():
            name_list = node.split('\'')
            name = next(n for n in name_list if n != '')
            if cp.__is_const_str(name) and name not in actions and \
               not cp.__is_const_num(name) and name not in numbers:
                str_list.append(name)
    failed = []
    if str_list:
        failed = similarity_select(fields, str_list)
    for elem in failed:
        elem_ = elem.replace('_', ' ')
        if elem_ in terms or elem_ in fields:
            failed.remove(elem)
    return failed


def get_messsage_row(sentence: str) -> MetaRecord:
    """ Query a meta record by sentence. """
    db = MetaDB()
    rows = db.get_meta_by_sentence(sentence)
    db.close_conn()
    return MetaRecord(rows[0][1], rows[0][0], *rows[0][2:])


def join_rows(message_row: MetaRecord, sentence_row: SentenceRecord) -> dict:
    """ Combine a MetaRecord and a SentenceRecord to a dict. """
    joined = {}
    joined.update(vars(message_row))
    joined.update(vars(sentence_row))
    return joined


def get_env_for_logic_form(lf: str) -> dict:
    """ Query environment dict for a LF. """
    try:
        db = SentenceDB()
        rows = db.get_mapping_by_lf(lf)
        sent_row = SentenceRecord(*rows[0])
        db.close_conn()
    except (IndexError, AttributeError):
        raise LookupError(f'No result in SentenceDB for logic form: "{lf}"')

    try:
        msg_row = get_messsage_row(sent_row.sentence)
    except (IndexError, AttributeError):
        raise LookupError(
            f'No result in MetaDB for sentence: "{sent_row.sentence}"')
    rows = join_rows(message_row=msg_row, sentence_row=sent_row)
    env = {}
    env['protocol'] = rows['protocol']
    env['message'] = rows['msg_type'].replace(' ', '_')
    env['field'] = rows['field']
    return env


def get_env_from_mds(msg_type: str, field: str, lf: str,
                     sent: str, sent_id: int) -> dict:
    """ Query environment dict from the MetaData System. """
    try:
        sent_row = get_sentence_row(msg_type, field, lf, sent, sent_id)
    except (IndexError, AttributeError):
        raise LookupError(f'No result in SentenceDB for '
                          f'"{msg_type}", "{lf}",'
                          f'"{sent}", "{sent_id}"')
    return json.loads(sent_row.env)


def get_proto_fields() -> dict:
    """ Get protocol, fields pairs.  """
    db = MetaDB()
    rows = db.get_all_meta()
    db.close_conn()
    proto_fields = defaultdict(set)
    for row in rows:
        proto, field, bit = row[0], row[3], row[4]
        if proto != 'unknown':
            proto_fields[proto].add((field, bit))
    #for proto in (p for p in proto_fields if p != 'unknown'):
    #    proto_fields[proto] -= proto_fields['unknown']
    return proto_fields


def get_msg_fields(message: str) -> list:
    """ Get field, size pairs of a given message.  """
    db = MetaDB()
    rows = db.get_all_meta()
    db.close_conn()
    message_fields = []
    for row in rows:
        proto, msg_type, field, bit = row[0], row[1], row[3], row[4]
        if msg_type == message and proto != 'unknown':
            message_fields.append((field, bit))
    return message_fields


def get_proto_messages(protocol: str) -> list:
    """ Get messages of a protocol. """
    db = MetaDB()
    rows = db.get_all_meta()
    db.close_conn()
    messages = set(row[1] for row in rows if row[0] == protocol)
    return messages


def get_message_envs_codes_sentences(message: str) -> list:
    """ Get all envs,codes and sentences for a given message.

    Parameters:
    message (str): name of message to search

    Returns:
    list of dict storing env, code, sentence, and sentence_id values
    of a SentenceRecord

    """
    sent_db = SentenceDB()
    sentence_recs = [SentenceRecord(*row)
                     for row in sent_db.get_all_mapping()]
    sent_db.close_conn()
    sent_records = [r for r in sentence_recs
                    if r.code and message in r.env]
    return [{'env': json.loads(r.env), 'code': r.code,
             'sentence': r.sentence, 'sentence_id': r.sentence_id}
            for r in sent_records]


def register_code_env(sentence_record: SentenceRecord, code: str, env: dict):
    """ Add generated code and environment to corresponding sentence
        record in mapping table.
    """
    sentence_record.code = code
    sentence_record.env = json.dumps(env)
    db = SentenceDB()
    db.replace_value(sentence_record)
    db.close_conn()


if __name__ == "__main__":
    argparser = argparse.ArgumentParser()
    argparser.add_argument(
        '--logicform', '-lf',
        help='Logic form to query',
    )
    args = argparser.parse_args()

    lf_env = {}
    lf_env.update(get_env_for_logic_form(args.logicform))

    print(f'    LF: {args.logicform}\n'
          f'   ENV: {lf_env}')
