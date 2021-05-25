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


class MetaRecord:
    """Record the information as metadata"""
    def __init__(self, msg_name, protocol="", txt="", field_name="",
                 bit_cnt=0, sentence="", sent_id=-1):
        self.protocol = protocol
        self.msg_type = msg_name
        self.msg_desc = txt
        self.field = field_name
        self.bit = bit_cnt
        self.sentence = sentence
        self.sentence_id = sent_id

    def __repr__(self):
        return (f'Record:\n'
                f' protocol: {self.protocol}\n'
                f' msg_type: {self.msg_type}\n'
                f' msg_desc: {self.msg_desc}\n'
                f' field: {self.field}\n'
                f' bit: {self.bit}\n'
                f' sentence: {self.sentence}\n'
                f' sentence_id: {self.sentence_id}\n')


class MetaDB:
    def __init__(self, name=None, create=True):
        if name is None:
            name = str(pathlib.Path(__file__).parent.absolute() / 'message.db')
        self.name = name
        self.conn = sqlite3.connect(name)
        self.cursor = self.conn.cursor()
        if create and self.table_empty():
            self.create_table()

    def table_empty(self):
        return os.stat(self.name).st_size == 0

    def close_conn(self):
        self.conn.close()

    def create_table(self):
        self.cursor.execute("""CREATE TABLE meta(
                               protocol text,
                               msg_type text,
                               msg_desc text,
                               field text,
                               bit integer,
                               sentence text,
                               sentence_id integer,
                               PRIMARY KEY (msg_type, field, sentence, sentence_id)
                              )""")
        self.conn.commit()

    def delete_value(self, data):
        with self.conn:
            self.cursor.execute("DELETE from meta WHERE msg_type=:msg_type AND msg_desc=:msg_desc "
                                "AND field=:field AND bit=:bit AND sentence=:sentence AND "
                                "sentence_id=:sentence_id",
                                {'msg_type': data.msg_type,
                                 'msg_desc': data.msg_desc,
                                 'field': data.field,
                                 'bit': data.bit,
                                 'sentence': data.sentence,
                                 'sentence_id': data.sentence_id})

    def delete_by_proto_msgtype_field_id(self, proto, msg_type, field, sent_id):
        with self.conn:
            self.cursor.execute("DELETE from meta WHERE "
                                "protocol=:protocol AND msg_type=:msg_type AND "
                                "field=:field AND sentence_id=:sentence_id",
                                {'protocol': proto, 'msg_type':msg_type,
                                 'field':field, 'sentence_id': sent_id})

    def delete_by_msg_type(self, msg_type):
        with self.conn:
            self.cursor.execute("DELETE from meta WHERE msg_type=:msg_type",
                                {'msg_type':msg_type})

    def delete_by_field(self, field):
        with self.conn:
            self.cursor.execute("DELETE from meta WHERE field=:field",
                                {'field':field})

    def delete_by_sentence(self, sentence):
        with self.conn:
            self.cursor.execute("DELETE from meta WHERE sentence=:sentence",
                                {'sentence':sentence})

    def delete_by_sentence_and_id(self, sentence, sentence_id):
        with self.conn:
            self.cursor.execute("DELETE from meta WHERE "
                                "sentence=:sentence AND sentence_id=:sentence_id",
                                {'sentence':sentence, 'sentence_id': sentence_id})

    def update_sentence(self, data, new_sentence):
        with self.conn:
            self.cursor.execute("UPDATE meta SET sentence=:sentence WHERE "
                                "msg_type=:msg_type AND msg_desc=:msg_desc AND "
                                "field=:field AND sentence_id=:sentence_id",
                                {'msg_type': data.msg_type, 'msg_desc': data.msg_desc,
                                 'field': data.field,
                                 'sentence': new_sentence, 'sentence_id': data.sentence_id})

    def update_sentence_and_id(self, data, sentence, sentence_id):
        with self.conn:
            self.cursor.execute("UPDATE meta "
                                "SET sentence=:sentence, sentence_id=:sentence_id WHERE "
                                "msg_type =:msg_type AND msg_desc AND "
                                "protocol=:protocol AND field=:field",
                                {'msg_type': data.msg_type, 'msg_desc': data.msg_desc,
                                 'field': data.field, 'protocol': data.protocol,
                                 'sentence': sentence, 'sentence_id': sentence_id})

    def update_desc(self, data, desc):
        with self.conn:
            self.cursor.execute("UPDATE meta SET msg_desc=:msg_desc "
                                "WHERE msg_type=:msg_type AND field=:field",
                                {'msg_type': data.msg_type, 'msg_desc': desc, 'field': data.field})

    def __add_value(self, data, operation='REPLACE'):
        with self.conn:
            cols = "(:protocol,:msg_type,:msg_desc,:field,:bit,:sentence,:sentence_id)"
            self.cursor.execute(f"{operation} INTO meta VALUES {cols}",
                                {'protocol':data.protocol,
                                 'msg_type': data.msg_type,
                                 'msg_desc': data.msg_desc,
                                 'field':data.field,
                                 'bit':data.bit,
                                 'sentence':data.sentence,
                                 'sentence_id':data.sentence_id,
                                })

    def insert_value(self, data):
        self.__add_value(data, operation='INSERT')

    def replace_value(self, data):
        self.__add_value(data, operation='REPLACE')

    def reset_db(self):
        os.remove(self.name)

    def get_meta_by_msg_type(self, msg_type):
        self.cursor.execute("SELECT * FROM meta WHERE msg_type=:msg_type", {'msg_type':msg_type})
        return self.cursor.fetchall()

    def get_meta_by_field(self, field):
        self.cursor.execute("SELECT * FROM meta WHERE field=:field", {'field':field})
        return self.cursor.fetchall()

    def get_meta_by_msg_type_and_field(self, msg_type, field):
        self.cursor.execute("SELECT * FROM meta WHERE msg_type=:msg_type AND field=:field",
                            {'msg_type': msg_type, 'field':field})
        return self.cursor.fetchall()

    def get_meta_by_proto_msgtype_field(self, proto, msg_type, field):
        self.cursor.execute("SELECT * FROM meta WHERE "
                            "msg_type=:msg_type AND field=:field AND protocol=:protocol",
                            {'msg_type': msg_type, 'protocol': proto, 'field': field})
        return self.cursor.fetchall()

    def get_meta_by_sentence(self, sentence):
        self.cursor.execute("SELECT * FROM meta WHERE sentence=:sentence",
                            {'sentence':sentence})
        return self.cursor.fetchall()

    def get_meta_by_sentence_and_id(self, sentence, sentence_id):
        self.cursor.execute("SELECT * FROM meta WHERE "
                            "sentence=:sentence AND sentence_id=:sentence_id",
                            {'sentence':sentence, 'sentence_id':sentence_id})
        return self.cursor.fetchone()

    def get_all_meta(self, with_header=False):
        self.cursor.execute("SELECT * FROM meta")
        header = tuple(d[0] for d in self.cursor.description)
        data = self.cursor.fetchall()
        if with_header:
            data.insert(0, header)
        return data

    def get_all(self, with_header=True):
        return self.get_all_meta(with_header)
