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


NAME="NTP UDP"
INPUT=ntp-udp.txt
PROTOCOL_NAME=NTP

# boilerplate stuff
pushd () {
    command pushd "$@" > /dev/null
}
popd () {
    command popd "$@" > /dev/null
}
CUR_DIR=`realpath $(dirname $BASH_SOURCE)`
SAGE_DIR="${CUR_DIR}/sage"
SAGE_BIN=sage
CCG_DICT="${SAGE_DIR}utils/ccg_tool/dictionary.py"
PRED_FILE="${SAGE_DIR}utils/logic_form_checker/check_predicates.py"

# init
function init_sage {
    echo "[$NAME] Init.."
    echo "[$NAME] Extracting tar.gz.."
    rm -rf ${SAGE_DIR}
    tar xfz ${CUR_DIR}/sage.tar.gz --no-same-owner -C ${CUR_DIR}
    reset_sage
}

# reset
function reset_sage {
    echo "[$NAME] Resetting.."
    rm -f ${CUR_DIR}/output.txt
    rm -f ${CUR_DIR}/${PROTOCOL_NAME}_*.h
    pushd $SAGE_DIR
    make clean build > /dev/null || make clean build
    popd
}

# run sage
function run_sage {
    echo "[$NAME] Executing.."
    pushd ${SAGE_DIR}
    cmd="./${SAGE_BIN} -i ${CUR_DIR}/${INPUT} -p ${PROTOCOL_NAME} > ${CUR_DIR}/output.txt"
    eval $cmd
    mv ${PROTOCOL_NAME}_hdr.h ${CUR_DIR}/${PROTOCOL_NAME}_hdr.h
    mv ${PROTOCOL_NAME}_gen.h ${CUR_DIR}/${PROTOCOL_NAME}_gen.h
    popd
    rm -f ${CUR_DIR}/nul
}

# analyze results
function check_results {
    echo "[$NAME] Checking results.."
    results=`diff -q <(grep "LF check summary:" ${CUR_DIR}/output.txt) ${CUR_DIR}/expected_output.txt`
    if [ "$results" ]; then
	echo "[$NAME] Check: LFs Diff Output:"
	diff <(grep "LF check summary:" ${CUR_DIR}/output.txt) ${CUR_DIR}/expected_output.txt
	echo "[$NAME] FAIL"
	return 1
    fi
    echo "[$NAME] Check: Logical Forms OK"
    # 2. check generated header
    results=`diff -q ${CUR_DIR}/${PROTOCOL_NAME}_hdr.h ${CUR_DIR}/expected_header.txt`
    if [ "$results" ]; then
	echo "[$NAME] Check: Header Diff Output:"
	diff ${CUR_DIR}/${PROTOCOL_NAME}_hdr.h ${CUR_DIR}/expected_header.txt
	echo "[$NAME] FAIL"
	return 1
    fi
    echo "[$NAME] Check: Headers OK"

    echo "[$NAME] OK"
    return 0
}

function auto_apply {
    echo "[$NAME] Auto applying changes.."
    echo "[$NAME] Adding new lexicon entries to the CCG tool:"
    diff --color -u ${SAGE_DIR}/utils/ccg_tool/dictionary.py ${CUR_DIR}/dictionary.py.new
    cp ${CUR_DIR}/dictionary.py.new ${SAGE_DIR}/utils/ccg_tool/dictionary.py
    echo "[$NAME] Adding new rules to the Logic Form Checker:"
    diff --color -u ${SAGE_DIR}/utils/logic_form_checker/check_predicates.py ${CUR_DIR}/check_predicates.py.new
    cp ${CUR_DIR}/check_predicates.py.new ${SAGE_DIR}/utils/logic_form_checker/check_predicates.py
}

function print_help {
cat<<EOF
Options:
init        Init a SAGE test environment
run         Run the experiment
autoapply   Automatically apply changes
-h /--help  Show this help
EOF
}


# MAIN
case $1 in
    "-h") print_help;;
    "--help") print_help;;
    "help") print_help;;
    "init") init_sage ;;
    "run") # check
	reset_sage
	run_sage
	res=$(check_results >&2)
	if [[ $res -ne 0 ]];
	then
	    echo "Looks like the results are still not ready: some sentences result no logical form"
	    echo "Please add new lexicon entries to the CCG tool in ${CCG_DICT}."
	    echo "Please add new rules to the Logic Form Checker at ${PRED_FILE}."
	    echo "Alternatively, you can let the script do the patching: ./run.sh autoapply"
	    echo "After your edits, please retry the execution: ./run.sh run"
	    exit 1
	fi
	echo "Done."
	exit 0
	;;
    "autoapply")
	auto_apply
	echo "Retry the execution as ./run.sh run"
	;;
    *) print_help;;
esac
