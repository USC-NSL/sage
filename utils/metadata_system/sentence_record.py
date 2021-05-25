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

import os
import pathlib
import sqlite3
import tempfile

import networkx

class SentenceRecord:

    def __init__(self, sentence, sent_id, msg_type='', field='',
                 label='', lf='', lf_graph='', env='', code=''):
        self.sentence = sentence
        self.sentence_id = sent_id
        self.msg_type = msg_type
        self.field = field
        self.label = label
        self.lf = lf
        self.lf_graph = lf_graph
        self.env = env
        self.code = code

    def __repr__(self):
        try:
            nodes = self.lf_graph.nodes()
            edges = self.lf_graph.edges()
        except:
            nodes = ''
            edges = ''
        return (f'sentence: {self.sentence}\n'
                f' sentence id: {str(self.sentence_id)}\n'
                f' message type: {self.msg_type}\n'
                f' label: {self.label}\n'
                f' logical form: {self.lf}\n'
                f' logical form graph nodes: {nodes}\n'
                f' logical form graph edges: {edges}\n'
                f' logical form processing env: {self.env}\n'
                f' code from logical form: {self.code}\n')


class SentenceDB:
    def __init__(self, name=None, create=True):
        if name is None:
            name = str(pathlib.Path(__file__).parent.absolute() / 'sent_to_lf.db')
        self.name = name
        self.conn = sqlite3.connect(name)
        self.cursor = self.conn.cursor()
        if create and self.table_empty():
            self.create_table()

    def table_empty(self):
        return os.stat(self.name).st_size == 0

    def reset_db(self):
        os.remove(self.name)

    def close_conn(self):
        self.conn.close()

    def create_table(self):
        self.cursor.execute("""CREATE TABLE mapping(
                            sentence text,
                            sentence_id integer,
                            msg_type text,
                            field text,
                            label text,
                            lf text,
                            lf_graph blob,
                            env text,
                            code text,
                            PRIMARY KEY (sentence, sentence_id, msg_type, field, lf)
                            )""")
        self.conn.commit()

    def delete_value(self, data):
        with self.conn:
            self.cursor.execute("DELETE from mapping "
                                "WHERE field=:field AND "
                                "sentence=:sentence AND sentence_id=:sentence_id",
                                {'field': data.field,
                                 'sentence': data.sentence,
                                 'sentence_id': data.sentence_id})

    def delete_bad(self, sentence, sentence_id, msg_type):
        with self.conn:
            self.cursor.execute("DELETE from mapping "
                                "WHERE msg_type=:msg_type AND field=:field AND "
                                "sentence=:sentence AND sentence_id=:sentence_id",
                                {'sentence': sentence, 'sentence_id': sentence_id,
                                 'msg_type': msg_type})

    def delete_empty_string_col(self):
        with self.conn:
            self.conn.execute("DELETE from mapping WHERE (lf IS NULL OR trim(lf)='')")

    def update_label(self, data, label):
        with self.conn:
            self.cursor.execute("UPDATE mapping SET label=:label WHERE sentence=:sentence",
                                {'sentence': data.sentence, 'label': label})

    def update_lf(self, data, lf):
        with self.conn:
            self.cursor.execute("UPDATE mapping SET lf=:lf WHERE "
                                "field=:field AND "
                                "sentence=:sentence AND sentence_id=:sentence_id""",
                                {'sentence': data.sentence, 'sentence_id': data.sentence_id,
                                 'lf': lf, 'field': data.field})

    def update_lf_graph(self, data, origin_lf_graph):
        content = ""
        with tempfile.TemporaryFile() as tmp:
            networkx.write_gpickle(origin_lf_graph, tmp)
            tmp.seek(0)
            content = tmp.read()
        with self.conn:
            self.cursor.execute("UPDATE mapping SET lf_graph=:lf_graph WHERE lf=:lf",
                                {'lf': data.lf, 'lf_graph': content})

    def update_code(self, field, sentence, sentence_id, lf, code):
        with self.conn:
            self.cursor.execute("UPDATE mapping SET code=:code WHERE "
                                "sentence=:sentence AND sentence_id=:sentence_id AND "
                                "field=:field AND lf=:lf",
                                {'sentence': sentence, 'sentence_id': sentence_id,
                                 'field': field, 'lf': lf, 'code': code})

    def __add_value(self, data, operation="REPLACE"):
        with self.conn:
            cols = "(:sentence,:sentence_id,:msg_type,:field,:label,:lf,:lf_graph,:env,:code)"
            self.cursor.execute(f"{operation} INTO mapping VALUES {cols}",
                                {'sentence': data.sentence,
                                 'sentence_id': data.sentence_id,
                                 'msg_type': data.msg_type,
                                 'field': data.field,
                                 'label': data.label,
                                 'lf': data.lf,
                                 'lf_graph': data.lf_graph,
                                 'env': data.env,
                                 'code': data.code,
                                })

    def insert_value(self, data):
        self.__add_value(data, 'INSERT')

    def replace_value(self, data):
        self.__add_value(data, 'REPLACE')

    def get_graph_by_sentence_and_id(self, sentence, sent_id):
        self.cursor.execute("SELECT lf_graph FROM mapping WHERE "
                            "sentence=:sentence AND sentence_id=:sentence_id",
                            {'sentence':sentence, 'sentence_id': sent_id})
        graph_pickle = self.cursor.fetchall()
        with tempfile.TemporaryFile() as tmp:
            tmp.write(graph_pickle[-1][-1])
            tmp.seek(0)
            lf_graph = networkx.read_gpickle(tmp)
        return lf_graph

    def get_mapping_by_msg_type(self, msg_type):
        self.cursor.execute("SELECT * FROM mapping WHERE msg_type=:msg_type",
                            {'msg_type': msg_type})
        return self.cursor.fetchall()

    def get_mapping_by_msg_sent_and_id(self, sentence, sent_id, msg_type):
        self.cursor.execute("SELECT * FROM mapping WHERE "
                            "sentence=:sentence AND sentence_id=:sentence_id AND "
                            "msg_type=:msg_type",
                            {'sentence':sentence, 'sentence_id': sent_id,
                             'msg_type': msg_type})
        return self.cursor.fetchall()

    def get_mapping_by_sentence_and_id(self, sentence, sent_id):
        # obsolete used in run_sqlite test_sentences() only
        self.cursor.execute("SELECT * FROM mapping WHERE "
                            "sentence=:sentence AND sentence_id=:sentence_id",
                            {'sentence':sentence, 'sentence_id': sent_id})
        return self.cursor.fetchall()

    def get_mapping_by_lf(self, lf):
        self.cursor.execute("SELECT * FROM mapping WHERE lf=:lf", {'lf': lf})
        return self.cursor.fetchall()

    def get_mapping_by_msgtype_lf_and_sent_with_id(self, msg_type, field, lf, sent, sent_id):
        self.cursor.execute("SELECT * FROM mapping WHERE "
                            "msg_type=:msg_type AND field=:field AND "
                            "lf=:lf AND sentence=:sentence AND sentence_id=:sentence_id",
                            {'msg_type': msg_type, 'field': field, 'lf': lf,
                             'sentence': sent, 'sentence_id': sent_id})
        return self.cursor.fetchall()

    def get_mapping_by_label(self, label):
        self.cursor.execute("SELECT * FROM mapping WHERE label=:label", {'label': label})
        return self.cursor.fetchall()

    def get_all_mapping(self, with_header=False):
        self.cursor.execute("SELECT * FROM mapping")
        header = tuple(d[0] for d in self.cursor.description)
        data = self.cursor.fetchall()
        if with_header:
            data.insert(0, header)
        return data

    def get_all(self, with_header=True):
        return self.get_all_mapping(with_header)
