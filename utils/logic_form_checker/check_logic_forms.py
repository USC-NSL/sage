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

import networkx

import check_equivalency as ce
import check_predicates as cp
import logic_form_graph as lfg


CHECKS = ('rules', 'order', 'sequence', 'duplicates')


def check_all(logic_forms: list, checks=None, verbose=False) -> list:
    """ Do all Logic Form Graph checking.

    Parameter:
    logic forms (list): logical forms
    verbose (bool): enable printing details

    Returns:
    lf_graphs (list): dicts of id (int) and a graph (LogicalFormGraph)

    """
    lf_graphs = lfg.create_logic_form_graphs_from_logic_forms(logic_forms)
    num_lfs = {'base': len(lf_graphs)}
    if verbose:
        print_all(lf_graphs)

    # check tree
    if not all(networkx.is_tree(g['graph'].graph) for g in lf_graphs):
        print("WARNING: not all Logic Form Graphs are trees!")

    # do checks
    if checks is None:
        checks = CHECKS
    for check in checks:
        lf_graphs = cp.check_pred_all(lf_graphs, mode=check)
        num_lfs[check] = len(lf_graphs)
        if verbose:
            print(f'# lfs after predicate {check}: {num_lfs[check]}')

    # check equivalency
    equivalent_ids = ce.check_logic_forms_eq(lf_graphs)
    elem_num = sum(len(id_set) for id_set in equivalent_ids)
    uniqlf_num = len(lf_graphs) - elem_num + len(equivalent_ids)
    num_lfs['unique'] = uniqlf_num
    if verbose:
        print('Numbers of unique lfs: ', uniqlf_num)
        sorted_ids = sorted([tuple(sorted(id_set))
                             for id_set in equivalent_ids])
        print(f'Equivalent logical forms: {sorted_ids}')
        print(f'LF check summary: {num_lfs}')

    return lf_graphs


def convert_all(logic_forms: list) -> list:
    """ Convert a logic forms to logic form graphs.

    Parameter:
    logic_forms (list): logical forms

    Returns:
    list of logical form graphs

    """
    return lfg.create_logic_form_graphs_from_logic_forms(logic_forms)


def print_all(lf_graphs: list):
    """ Print all Logical Form Graph.

    Parameter:
    lf_graphs (list): logical form graphs

    """
    for lf_g in lf_graphs:
        print(f'{lf_g["id"]}: {lf_g["graph"].logic_form}')


def export_all(lf_graphs: list, **kwargs):
    """ Export all Logic Form Graph.

    Parameter:
    lf_graphs (list): logical form graphs

    """
    ce.export_all(lf_graphs, **kwargs)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument(
        'logicforms',
        help='Logic forms to process',
        nargs='+', default=[],
    )
    parser.add_argument(
        '--quiet', '-q',
        help='Surpress verbose mode',
        action='store_true',
    )
    args = parser.parse_args()

    logic_form_graphs = check_all(args.logicforms, verbose=not args.quiet)

    print('Final logical forms:')
    print_all(logic_form_graphs)
