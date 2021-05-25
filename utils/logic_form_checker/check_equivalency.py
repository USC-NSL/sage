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
import itertools
import pathlib
import subprocess
import tempfile

import networkx

import logic_form_graph as lfg


def check_logic_forms_eq_pair(lfs: list):
    """Check equivalency of logic forms pairwise.

    Parameter:
    lfs (list): dicts of id (int) and a graph (LogicalFormGraph)

    Returns:
    isomorph_pares (list): tuples with ids of equivalent logic forms

    """
    isomorph_pares = []
    for logic_form1, logic_form2 in itertools.combinations(lfs, 2):
        if networkx.is_isomorphic(logic_form1['graph'].graph,
                                  logic_form2['graph'].graph):
            isomorph_pares.append((logic_form1['id'], logic_form2['id']))
    return isomorph_pares


def check_logic_forms_eq(lfs: list):
    """Check equivalency of logic forms.

    Parameter:
    lfs (list): dicts of id (int) and a graph (LogicalFormGraph)

    Returns:
    equivalent_ids (list): sets with ids of equivalent logic forms

    """
    eq_pairs = map(set, check_logic_forms_eq_pair(lfs))
    equivalent_ids = []
    for ids in eq_pairs:
        for id_set in equivalent_ids:
            if not ids.isdisjoint(id_set):
                id_set.update(ids)
                break
        else:
            equivalent_ids.append(ids)
    return equivalent_ids


def print_logic_form_list(logic_forms: list):
    """ Print list of logic forms. """
    print('* Sentences')
    for logic_form in logic_forms:
        print(f' {logic_form["id"]}: {logic_form["graph"].sentence}')


def print_equal_logic_forms(logic_forms: list):
    """ Print ids of equivalent logic forms. """
    print('* Results')
    eq_ids = check_logic_forms_eq(logic_forms)
    sorted_ids = sorted([tuple(sorted(id_set)) for id_set in eq_ids])
    print(f'Equal logical forms: {sorted_ids}')


def print_all(logic_forms: list):
    """ Print detailed logic form analysis. """
    print_logic_form_list(logic_forms)
    print_equal_logic_forms(logic_forms)
    export_all(logic_forms)


def export_all(logic_forms: list, basename='lfg',
               out_dir='/tmp', out_format='png'):
    """ Export logic form graphs to png files. """
    with tempfile.NamedTemporaryFile() as dotfile:
        for logic_form in logic_forms:
            logic_form['graph'].write_dot(dotfile.name)
            out_basename = f'{basename}-{logic_form["id"]}.{out_format}'
            out_file = pathlib.Path(out_dir, out_basename)
            cmd = f'dot -T{out_format} {dotfile.name} -o {out_file}'.split()
            subprocess.run(cmd, check=True)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument(
        'logicforms',
        help='Logic forms to process',
        nargs='+', default=[],
    )
    parser.add_argument(
        '--export', '-e',
        help='Export LogicFormGraphs to files at /tmp/lgf-{}',
        action='store_true',
    )
    args = parser.parse_args()

    lf_graphs = lfg.create_logic_form_graphs_from_logic_forms(args.logicforms)
    print_all(lf_graphs)
    if args.export:
        export_all(lf_graphs)
