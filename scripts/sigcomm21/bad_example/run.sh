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


NAME="ICMP Echo"
INPUT=bad_echo.txt
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
CCG_DIR="${SAGE_DIR}utils/ccg_tool/"
CCG_DIC="${SAGE_DIR}utils/ccg_tool/dictionary.py"
CCG_BIN=parse_rfc.py
META_DIR="${SAGE_DIR}utils/metadata_system"
META_BIN=run_sqlite.py
PRED_FILE="${SAGE_DIR}utils/logic_form_checker/check_predicates.py"

# highlight color
RED='\033[0;31m'
NC='\033[0m' # No Color

# reset
echo "[$NAME] Resetting.."
rm -f ${CUR_DIR}/output.txt
rm -f ${CUR_DIR}/ICMP_*.h
rm -f ${CUR_DIR}/sent_to_lf.db
pushd $SAGE_DIR
make clean build > /dev/null || make clean build
popd


# run sage
echo "[$NAME] Executing.."
pushd ${SAGE_DIR}
cmd="./${SAGE_BIN} -i ${CUR_DIR}/${INPUT} -p ${PROTOCOL_NAME} -l > ${CUR_DIR}/output.txt"
eval $cmd
mv ${PROTOCOL_NAME}_hdr.h ${CUR_DIR}/${PROTOCOL_NAME}_hdr.h
popd
rm -f ${CUR_DIR}/nul


# analyze results
# 1. check logical forms
echo "[$NAME] Checking results.."
results=$(awk -F'[,:}]' '$12 ~ /unique/ && $13 != 1 {print $0;}' ${CUR_DIR}/output.txt)
zero_results=$(sed -n "/Sentence to CCG/{p; n;p;}" output.txt | sed -n -e '/IR numbers: /{x;d}' -e '/:/{x;p;d}' -e x | sed -n "/Sentence to CCG/{p;}")

if [ "$zero_results" ]; then
    echo "[$NAME] Check: Sentence(s) cannot generate LF before disambiguation:"
    zero_sentence=$(echo $zero_results | awk -F":" '{print $2}' | sed -e 's/^[[:space:]]*//')
    echo -e "\t ${RED}$zero_sentence${NC}"
    echo "[$NAME] Require Manual Input! Suggestions as Follows:"
    echo "[$NAME] Please review the following analysis of CCG parsing and add/change lexicons in ${CCG_DIC}."
    pushd $CCG_DIR
    cmd="python3 $CCG_BIN -dd -s \"$zero_sentence\""
    analysis=$(eval $cmd)
    echo -e "${RED}$analysis${NC}"
    echo -e "[$NAME] For demo purpose, if the sentence is revised by assigning 'bad' with 'NP' lexicon, CCG parsing will produce result."
    popd
    echo "[$NAME] FAIL"
fi

if [ "$results" ]; then
    echo "[$NAME] Check: LFs Ambiguous Output:"
    echo -e "\t ${RED}$results${NC}"
    echo "[$NAME] Require Manual Input! Suggestions as Follows:"
    lf_0=$(echo $results | awk -F'[,:}]' '$12 ~ /unique/ && $13 == 0 {print $0;}')
    lf_mult=$(echo $results | awk -F'[,:}]' '$12 ~ /unique/ && $13 > 0 {print $0;}')

    if [ "$lf_0" ]; then
      echo "[$NAME] 0 LF sentence exists. This might due to missing lexicons or conflicting disambiguation checks:"
      echo "[$NAME] Please view execution log 'output.txt' for the 0LF sentence."
      echo "[$NAME] To add lexicon, please edit ${CCG_DIC}."
      echo "[$NAME] To check disambiguation rules, please view and edit ${PRED_FILE}."
    fi

    if [ "$lf_mult" ]; then
      echo "[$NAME] More than 1 LF sentence exists. Please rewrite below sentence(s):"
      target=$(sed -n "/$lf_mult/{n; n;p;}" ${CUR_DIR}/output.txt)
      target_lf=$(echo $target | awk -F'[:}]' '{print $2;}')
      target_lf_no_lead_space="$(echo -e "${target_lf}" | sed -e 's/^[[:space:]]*//')"
      pushd $META_DIR
      cmd="python3 $META_BIN -gs -lf \"$target_lf_no_lead_space\""
      final=$(eval $cmd)
      echo -e "\t ${RED}$final${NC}"
      echo "[$NAME] Full execution log is kept in file 'output.txt'"
      echo "[$NAME] For demo purpose, if the sentence is revised by replacing comma with period. This program should not give any alarm."
      popd
      #echo $target_lf
    fi
    echo "[$NAME] FAIL"
    exit 1
fi
echo "[$NAME] Check: Logical Forms OK"
# 2. check generated header
results=`diff -q ${CUR_DIR}/${PROTOCOL_NAME}_hdr.h ${CUR_DIR}/expected_header.txt`
if [ "$results" ]; then
    echo "[$NAME] Check: Header Diff Output:"
    diff ${CUR_DIR}/${PROTOCOL_NAME}_hdr.h ${CUR_DIR}/expected_header.txt
    echo "[$NAME] FAIL"
    exit 1
fi
echo "[$NAME] Check: Headers OK"

echo "[$NAME] OK"
exit 0
