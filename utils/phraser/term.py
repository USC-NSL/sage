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


class TermDB:
    def __init__(self, name=None, create=True):
        if name is None:
            name = str(pathlib.Path(__file__).parent.absolute() / 'term.db')
        self.name = name
        self.conn = sqlite3.connect(name)
        self.cursor = self.conn.cursor()
        if create and self.table_empty():
            self.create_table()
            self.import_dic()

    def table_empty(self):
        return os.stat(self.name).st_size == 0

    def close_conn(self):
        self.conn.close()

    def create_table(self):
        self.cursor.execute("""CREATE TABLE term(
                          first_word  text,
                          noun_phrase text,
                          PRIMARY KEY (first_word, noun_phrase)
                          )""")
        self.conn.commit()

    def import_dic(self):
        cwd = pathlib.Path(__file__).parent.absolute()
        dic_path = cwd / 'data' / 'EN' / 'custom.txt'
        # new change to add state constants
        state_path = cwd / 'data' / 'EN' / 'stateval.txt'

        with open(dic_path, 'r') as term_dic:
            print("Open term dic successfully")
            line = term_dic.readline()
            while line:
                line = line.rstrip("\n")
                first, second = parse_str(line)
                self.insert_value(first, second)
                line = term_dic.readline()

        with open(state_path, 'r') as state_dic:
            print("Open state value dic successfully")
            line = state_dic.readline()
            while line:
                line = line.rstrip("\n")
                first, second = parse_str(line)
                self.insert_value(first, second)
                line = state_dic.readline()

        print("Done with importing term dic")

    def insert_value(self, first_word, noun_phrase):
        with self.conn:
            self.cursor.execute(
                "INSERT INTO term VALUES (:first_word,:noun_phrase)",
                {'first_word': first_word, 'noun_phrase': noun_phrase})

    def reset_db(self):
        os.remove(self.name)

    def get_term_by_first_word(self, first_word):
        self.cursor.execute(
            "SELECT * FROM term WHERE first_word=:first_word",
            {'first_word': first_word})
        return self.cursor.fetchall()

    def get_all_term(self):
        self.cursor.execute("SELECT * FROM term")
        return self.cursor.fetchall()


def parse_str(sentence):
    sent_lower = sentence.lower()
    sent_first = sent_lower.split()[0]
    return sent_first, sent_lower


def test_TermDB():
    """ Simple test of TermDB features """
    term_db = TermDB()
    first, second = parse_str("USCNSL is awesome")
    print(term_db.get_term_by_first_word("abc"))


if __name__ == "__main__":
    term_db = TermDB()
    term_db.reset_db()
