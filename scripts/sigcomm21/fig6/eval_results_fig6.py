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

from tabulate import tabulate


LFCHECK_PATTERN = "LF check summary"
CHECKS = {
    "base": "Base",
    "rules": "Type",
    "order": "Argument Ordering",
    "sequence": "Predicate Ordering",
    "duplicates": "Distributivity",
    "unique": "Associativity",
}


def collect_results(sage_output_textiowrapper, lfcheck_pattern=LFCHECK_PATTERN) -> list:
    """ Collects LF parsing results from SAGE output. """
    file_content = sage_output_textiowrapper.readlines()
    results = []
    for line in file_content:
        if lfcheck_pattern in line:
            new_line = line.replace("LF check summary: ", "")
            results.append(json.loads(new_line.replace("'", "\"")))
    return results


def eval_results(results: list, check: str) -> dict:
    """ Calculate statistics of LF parsing results. """
    stat_dict = {}
    diffs = [r["base"] - r[check] for r in results]
    assert all(e >= 0 for e in diffs)
    len_diffs = sum(1 for e in diffs if e > 0)
    stat_dict["lfs"] = sum(diffs) / len_diffs
    stat_dict["sentences"] = len_diffs
    return stat_dict


if __name__ == "__main__":
    PARSER = argparse.ArgumentParser()
    PARSER.add_argument('sageoutput', type=argparse.FileType('r'),
                        help='SAGE output as a file')
    PARSER.add_argument('-c', '--check', type=str,
                        help='Check names', choices=CHECKS)
    args = PARSER.parse_args()
    res = collect_results(args.sageoutput)
    stats = eval_results(res, args.check)
    stats['check'] = CHECKS[args.check]
    CUR_DIR = pathlib.Path(__file__).parent.absolute()
    res_file = CUR_DIR / "expected_results.txt"
    with open(res_file) as expfile:
        expected_res = json.load(expfile)
    expected_stat = next(e for e in expected_res
                         if e["check"] == CHECKS[args.check])
    expected_stat['mode'] = "Figure"
    stats['mode'] = "Measured"
    columns = {
        'mode': ' ',
        #'check': 'Check',
        'lfs': '#LFs / Sentence',
        'sentences': 'Sentences'
    }
    print(f"* {CHECKS[args.check]}")
    print(tabulate([{columns[e]: expected_stat[e] for e in columns},
                    {columns[e]: stats[e] for e in columns}],
                   headers='keys', numalign='right',
                   floatfmt=".2f", tablefmt='orgtbl'),
          '\n')
