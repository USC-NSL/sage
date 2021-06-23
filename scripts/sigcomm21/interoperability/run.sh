#!/bin/bash

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


NAME="ICMP"
INPUT=rfc792.txt
PROTOCOL_NAME=icmp

# boilerplate stuff
pushd () {
    command pushd "$@" > /dev/null
}
popd () {
    command popd "$@" > /dev/null
}
CUR_DIR=`realpath $(dirname $BASH_SOURCE)`
SAGE_DIR="${CUR_DIR}/../../../"
SAGE_BIN=sage

# reset
echo "[$NAME] Resetting.."
rm -f ${CUR_DIR}/output.txt
rm -f ${CUR_DIR}/${PROTOCOL_NAME}_*.h
rm -f ${CUR_DIR}/gen.h
pushd $SAGE_DIR
make clean build > /dev/null || make clean build
popd


# run sage
echo "[$NAME] Executing.."
pushd ${SAGE_DIR}
cmd="./${SAGE_BIN} -i ${CUR_DIR}/${INPUT} -p ${PROTOCOL_NAME} -o > output.txt"
eval $cmd
echo "[$NAME] Done with Code Generation..."
mv ${PROTOCOL_NAME}_hdr.h ${CUR_DIR}/${PROTOCOL_NAME}_hdr.h
mv ${PROTOCOL_NAME}_gen.h ${CUR_DIR}/${PROTOCOL_NAME}_gen.h
popd
rm -f ${CUR_DIR}/nul

# patching header
echo "[$NAME] Patching Header..."
sed -i -E "s/#endif  \/\/ (.+)/#endif  \/\* \1 \*\//" ${PROTOCOL_NAME}_hdr.h
sed -i "/\/\//d" ${PROTOCOL_NAME}_hdr.h


# patching generated code
echo "[$NAME] Patching Code..."
mv ${PROTOCOL_NAME}_gen.h gen.h
sed -i -E "s/#endif  \/\/ (.+)/#endif  \/\* \1 \*\//" gen.h
sed -i "/\/\//d" gen.h
sed -i "s/${NAME}_GEN_H_/GEN_H_/g" gen.h
include_guard="#include \"helper.h\"\n#include \"icmp_hdr.h\"\n#include \"meta.h\"\n#include \"proto.h\"\n"
sed -i "/#define GEN_H_/a\\$include_guard" gen.h

# analyze results
# 1. check generated header
echo "[$NAME] Check: Header.."
results=`diff -q ${CUR_DIR}/${PROTOCOL_NAME}_hdr.h ${CUR_DIR}/expected_header.h`
if [ "$results" ]; then
    echo "[$NAME] Check: Header Diff Output:"
    diff ${CUR_DIR}/${PROTOCOL_NAME}_hdr.h ${CUR_DIR}/expected_header.h
    echo "[$NAME] FAIL"
    exit 1
fi
echo "[$NAME] Check: Headers OK"
# . check generated code
echo "[$NAME] Check: Code OK"
results=`diff -q ${CUR_DIR}/gen.h ${CUR_DIR}/expected_code.h`
if [ "$results" ]; then
    echo "[$NAME] Check: Code Diff Output:"
    diff ${CUR_DIR}/gen.h ${CUR_DIR}/expected_code.h
    echo "[$NAME] FAIL"
    exit 1
fi
echo "[$NAME] OK"
exit 0
