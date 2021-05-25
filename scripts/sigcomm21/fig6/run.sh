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
PROTOCOL_NAME=ICMP

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
rm -f ${CUR_DIR}/output_*.txt
rm -f ${CUR_DIR}/icmp_*.h
pushd $SAGE_DIR
make clean build > /dev/null || make clean build
popd

# Checks:
# rules - Type
# order - Argument Ordering
# sequence - Predicate Ordering
# duplicates - Distributivity

# run sage
echo "[$NAME] Executing.."
pushd ${SAGE_DIR}
for check in rules order sequence duplicates
do
    # quick reset
    make clean build > /dev/null || make clean build
    # run sage
    echo "[$NAME] Testing Check ${check}.."
    cmd="./${SAGE_BIN} -i ${CUR_DIR}/${INPUT} -p ${PROTOCOL_NAME} -c ${check} > ${CUR_DIR}/output_${check}.txt"
    eval $cmd
    mv ${PROTOCOL_NAME}_hdr.h ${CUR_DIR}/${PROTOCOL_NAME}_hdr.h
    mv ${PROTOCOL_NAME}_gen.h ${CUR_DIR}/${PROTOCOL_NAME}_gen.h
    rm -f ${CUR_DIR}/nul
done
popd

# analyze results
echo "[$NAME] Checking results.."
for check in rules order sequence duplicates
do
    python3 ${CUR_DIR}/eval_results_fig6.py ${CUR_DIR}/output_${check}.txt -c ${check}
done
