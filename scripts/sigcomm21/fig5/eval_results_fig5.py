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


def eval_results(results: list) -> dict:
    """ Calculate basic descriptive statistics of LF parsing results. """
    data = {check: [r[check] for r in results] for check in CHECKS}
    stats = {paper_check: {} for paper_check in CHECKS.values()}
    for check, paper_check in CHECKS.items():
        stats[paper_check]['min'] = min(data[check])
        stats[paper_check]['max'] = max(data[check])
        stats[paper_check]['avg'] = sum(data[check]) / len(data[check])
    return stats


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('sageoutput', type=argparse.FileType('r'),
                        help='SAGE output as a file')
    parser.add_argument('-p', '--proto', type=str,
                        help='Protocol name', choices=['icmp', 'igmp', 'bfd'])
    args = parser.parse_args()
    res = collect_results(args.sageoutput)
    stats = eval_results(res)
    CUR_DIR = pathlib.Path(__file__).parent.absolute()
    res_file = CUR_DIR / f'{args.proto}_expected.txt'
    with open(res_file) as expfile:
        expected_res = json.load(expfile)
    check_order = ("Base", "Type", "Argument Ordering", "Predicate Ordering",
                   "Distributivity", "Associativity")
    meas_columns = {
        'check': 'Check',
        'min': 'Min(measured)',
        'avg': 'Avg(measured)',
        'max': 'Max(measured)',
    }
    fig_columns = {
        'check': 'Check',
        'min': 'Min(figure)',
        'avg': 'Avg(figure)',
        'max': 'Max(figure)',
    }
    for check in check_order:
        stats[check]['check'] = check
    meas_data = [stats[check] for check in check_order]
    mdata = [{meas_columns[e]:d[e] for e in meas_columns} for d in meas_data]
    fdata = [{fig_columns[e]:d[e] for e in fig_columns} for d in expected_res]
    all_data = [dict(list(m.items()) + list(f.items())) for m, f in zip(mdata, fdata)]

    print(f"* {args.proto.upper()}")
    print(tabulate(all_data,
                   headers='keys', numalign='right', floatfmt=".2f", tablefmt='orgtbl'),
          '\n')
