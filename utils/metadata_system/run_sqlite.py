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
import pathlib
import sys

from metarecord import MetaRecord, MetaDB
from sentence_record import SentenceRecord, SentenceDB

CUR_DIR = pathlib.Path(__file__).parent.absolute()

UTILS_DIR = CUR_DIR / '..'
sys.path.insert(0, str(UTILS_DIR))
from similarity import similarity_map

LFC_DIR = CUR_DIR / '..' / 'logic_form_checker'
sys.path.insert(0, str(LFC_DIR))
import logic_form_graph as lfg

def get_argparse():
    arg_parser = argparse.ArgumentParser()
    arg_parser.add_argument(
        '--test', '-t',
        help='test metaDB and sentenceDB',
        action="store_true"
    )
    arg_parser.add_argument(
        '--create_stack', '-c',
        help='create message protocol stack',
        action="store_true"
    )
    arg_parser.add_argument(
        '--clean_invalid', '-ci',
        help='clean invalid sentenceDB entry',
        action='store_true',
    )
    arg_parser.add_argument(
        '--message_type', '-m',
        help="register message type",
        default="msg_type"
    )
    arg_parser.add_argument(
        '--name_reg', '-n',
        help='register field name',
        default="field_name"
    )
    arg_parser.add_argument(
        '--bit_reg', '-b',
        help='register field bit',
        default=0
    )
    arg_parser.add_argument(
        '--proto_reg', '-p',
        help='register protocol',
        default='',
    )
    arg_parser.add_argument(
        '--sent_reg', '-s',
        help='register sentence',
        default='',
    )
    arg_parser.add_argument(
        '--sentid_reg', '-i',
        help='register sentence id',
        default=-1,
    )
    arg_parser.add_argument(
        '--env_reg', '-env',
        help='register env',
        default='',
    )
    arg_parser.add_argument(
        '--lf_reg', '-lf',
        help='register lf',
        default='',
    )
    arg_parser.add_argument(
        '--label_reg', '-l',
        help='register sentence label',
        default='',
    )
    arg_parser.add_argument(
        '--update_lf', '-ulf',
        help='update lf and lf id for assignment case',
        action='store_true',
    )
    arg_parser.add_argument(
        '--update_sent', '-us',
        help='flag to update sentence and sentence id',
        action='store_true',
    )
    arg_parser.add_argument(
        '--update_label', '-ul',
        help='flag to update sentence label',
        action='store_true',
    )
    arg_parser.add_argument(
        '--update_description', '-ud',
        help='flag to update description',
        action="store_true"
    )
    arg_parser.add_argument(
        '--description', '-desc',
        help='register description',
    )
    arg_parser.add_argument(
        '--dump_meta', '-dm',
        help='dump all entries in metaDB',
        action="store_true"
    )
    arg_parser.add_argument(
        '--dump_sent', '-ds',
        help='dump all entries in sentenceDB',
        action="store_true"
    )
    arg_parser.add_argument(
        '--dump_format', '-df',
        help='Format to use dump tables',
        choices=['csv', 'tsv', 'org'],
        default='csv',
        type=str,
    )
    arg_parser.add_argument(
        '--reset_db', '-r',
        help='Clear metaDB and sentenceDB data',
        action="store_true"
    )
    arg_parser.add_argument(
        '--set_table1_name', '-s1',
        help='set metaDB name',
        default='message.db'
    )
    arg_parser.add_argument(
        '--set_table2_name', '-s2',
        help='set sentenceDB name',
        default='sent_to_lf.db'
    )
    arg_parser.add_argument(
        '--get_sentence', '-gs',
        help='get sentence by lf',
        action="store_true",
    )
    return arg_parser


def register_table1(proto, msg, field, bit, name=None):
    meta_db = MetaDB(name)
    meta_1 = MetaRecord(protocol=proto, msg_name=msg, field_name=field, bit_cnt=bit)
    meta_db.replace_value(meta_1)


def add_sent_table1(msg, field, bit, sent, sent_id, name=None):
    meta_db = MetaDB(name)
    meta_1 = MetaRecord(msg_name=msg, field_name=field, bit_cnt=bit,
                        sentence=sent, sent_id=sent_id)
    meta_db.replace_value(meta_1)


def add_sentence_to_meta(table1, protocol, msg_type, field_name,
                         bit_cnt, sentence, sentence_id):
    """ Add sentence and sentence id to an existing message type and field. """
    get_sent_id = -2
    meta_db = MetaDB(table1)
    msg_meta = meta_db.get_meta_by_proto_msgtype_field(protocol, msg_type, field_name)
    try:
        bit_cnt = msg_meta[0][4]
        desc = msg_meta[0][2]
        get_sent_id = msg_meta[0][6]
    except IndexError:
        protocol = 'unknown'
        desc = ''
        bit_cnt = -1
    meta_db.replace_value(MetaRecord(protocol=protocol,
                                     msg_name=msg_type,
                                     txt=desc,
                                     field_name=field_name,
                                     bit_cnt=bit_cnt,
                                     sentence=sentence,
                                     sent_id=sentence_id))
    if get_sent_id == -1:
        meta_db.delete_by_proto_msgtype_field_id(protocol, msg_type, field_name, -1)


def add_sentence_to_mapping(table2, msg, field, sentence, sentence_id):
    sentence_db = SentenceDB(table2)
    sentence_db.replace_value(SentenceRecord(sentence, sentence_id,
                                             msg_type=msg, field=field))


def add_label_to_mapping(table2, msg, field, sentence, sentence_id, sentence_label):
    sentence_db = SentenceDB(table2)
    sentence_db.replace_value(SentenceRecord(sentence, sentence_id,
                                             msg_type=msg, field=field,
                                             label=sentence_label))


def update_lf(table2, msg, field, sentence, sentence_id, lf_in, env_in):
    sentence_db = SentenceDB(table2)
    sent_rec = SentenceRecord(sentence=sentence, sent_id=sentence_id,
                              msg_type=msg, field=field,
                              lf=lf_in, env=env_in)
    sentence_db.replace_value(sent_rec)


def clean_bad_entry(table2, msg, sentence, sentence_id):
    sentence_db = SentenceDB(table2)
    sentence_db.delete_bad(sentence, sentence_id, msg)
    sentence_db.delete_empty_string_col()


def update_meta_sent(proto, msg_type, field, sent, sent_id, name):
    meta_db = MetaDB(name)
    entries = meta_db.get_meta_by_proto_msgtype_field(proto, msg_type, field)
    ids = [row[6] for row in entries]
    desc = entries[0][2]
    bit = entries[0][4]

    if -1 in ids:
        meta_db.delete_by_proto_msgtype_field_id(proto, msg_type, field, -1)

    if sent_id not in ids:
        mr = MetaRecord(msg_type, proto, desc, field, bit, sent, sent_id)
        meta_db.insert_value(mr)


def update_desc(msg_type, field, desc, name='message.db'):
    meta_db = MetaDB(name)
    entries = meta_db.get_meta_by_msg_type(msg_type)
    all_fields = [row[3] for row in entries]
    match_status, matched_field = similarity_map(all_fields, field)
    if match_status:
        mr = MetaRecord(msg_type, field_name=matched_field)
        meta_db.update_desc(mr, desc)
    else:
        field = field.lstrip(' ')
        register_table1('unknown', msg_type, field, -1, name)
        mr = MetaRecord(msg_type, field_name=field)
        meta_db.update_desc(mr, desc)


def format_table(columns: list, table_data: list, mode='org') -> str:
    """ Represent table data in a well-formatted way.

    Parameters:
    columns (list): table columns
    table_data (list): table content
    mode (str): output format (csv,tsv,org)

    Returns:
    string representation of table data

    """
    spec_chars = {
        'org': {'sep': ' | ', 'eol': ' |\n', 'sol': '| '},
        'csv': {'sep': ',', 'eol': '\n'},
        'tsv': {'sep': '\t', 'eol': '\n'},
        'tex': {'sep': ' & ', 'eol': '\\\\n'},
    }
    sep = spec_chars[mode].get('sep', ' ')    # separator
    eol = spec_chars[mode].get('eol', '\n')    # end of line
    sol = spec_chars[mode].get('sol', '')    # start of line
    header = '%s%s%s' % (sol, sep.join(columns), eol)
    format_list = ['%s' for _ in columns]
    row_format = f'{sol}{sep.join(format_list)}{eol}'
    rows = (row_format % row for row in table_data)
    table = header
    table += ''.join(rows)
    return table


def __dump_table(db, out_format='csv') -> str:
    all_entries = db.get_all()
    formatted_table = format_table(all_entries[0], all_entries[1:],
                                   mode=out_format)
    return formatted_table


def dump_table1(name=None, out_format="csv"):
    meta_db = MetaDB(name)
    table_dump = __dump_table(meta_db, out_format=out_format)
    meta_db.close_conn()
    print(table_dump)


def dump_table2(name=None, out_format="csv"):
    sent_db = SentenceDB(name)
    table_dump = __dump_table(sent_db, out_format=out_format)
    sent_db.close_conn()
    print(table_dump)


def reset_tables(table1=None, table2=None):
    meta_db = MetaDB(table1)
    sent_db = SentenceDB(table2)
    for db in (meta_db, sent_db):
        db.reset_db()


def get_sentence_from_lf(lf, name=None):
    sent_db = SentenceDB(name)
    sent_data = sent_db.get_mapping_by_lf(lf)
    sent = sent_data[0][0]
    return sent


if __name__ == "__main__":
    argparser = get_argparse()
    args = argparser.parse_args()
    table1_name = args.set_table1_name
    table2_name = args.set_table2_name
    proto = args.proto_reg
    msg_type = args.message_type
    field_name = args.name_reg
    field_bit = args.bit_reg
    sentence = args.sent_reg
    sentence_id = args.sentid_reg
    lf = args.lf_reg
    env = args.env_reg

    if args.test:
        test_metaDB()
        test_sentenceDB()

    if args.create_stack:
        register_table1(proto, msg_type, field_name, field_bit, name=table1_name)

    if args.update_description:
        msg_type = args.message_type
        tbm_field_name = args.name_reg
        desc = args.description
        update_desc(msg_type, tbm_field_name, desc, name=table1_name)

    if args.update_sent:
        proto = args.proto_reg
        msg_type = args.message_type
        field_name = args.name_reg
        sent = args.sent_reg
        sent_id = args.sentid_reg
        update_meta_sent(proto, msg_type, field_name, sent, sent_id, name=table1_name)

    if args.sent_reg and args.sentid_reg and not args.update_label \
       and not args.clean_invalid and not args.update_lf:
        add_sentence_to_meta(table1_name, proto, msg_type, field_name, field_bit,
                             sentence, sentence_id)

    if args.update_label:
        add_label_to_mapping(table2_name, msg_type, field_name,
                             sentence, sentence_id, args.label_reg)

    if args.clean_invalid:
        clean_bad_entry(table2_name, msg_type, sentence, sentence_id)

    if args.update_lf:
        update_lf(table2_name, msg_type, field_name,
                  sentence, sentence_id, lf, env)

    if args.dump_meta:
        dump_table1(name=table1_name, out_format=args.dump_format)

    if args.dump_sent:
        dump_table2(name=table2_name, out_format=args.dump_format)

    if args.reset_db:
        reset_tables(table1=table1_name, table2=table2_name)

    if args.get_sentence:
        try:
            print(get_sentence_from_lf(lf, name=table2_name))
        except:
            print("Error: cannot find the original sentence by this LF")
