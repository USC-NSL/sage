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

WARNINGS=-Wall
OPT_LVL=0
CXX=g++
CXXFLAGS= $(WARNINGS) -O$(OPT_LVL) --std=c++11

LIBS=-l sqlite3

.PHONY: clean purge format

default: build

format:
	clang-format --style=file -i *.cpp
	clang-format --style=file -i *.h

build: sage

sage: parser.cpp
	 $(CXX) $(CXXFLAGS) -o $@ $^ $(LIBS)

clean:
	rm -f *_gen.h
	rm -f *_hdr.h
	rm -f *_fields.txt
	rm -f utils/code_generator/code_out.txt
	rm -f utils/phraser/nul
	rm -f utils/phraser/models/DBLP/output.txt
	rm -f utils/ccg_tool/nul
	rm -f utils/ccg_tool/CCGresult.txt
	#cd utils/metadata_system && python3 run_sqlite.py -r
	rm -f utils/metadata_system/message.db
	rm -f utils/metadata_system/sent_to_lf.db
	#cd utils/phraser && python3 term.py
	rm -f utils/phraser/term.db
	rm -f bfd-lf.txt
	rm -f state_code.txt
	rm -f utils/code_generator/dyn_term.py

purge: clean
	rm -f sage
