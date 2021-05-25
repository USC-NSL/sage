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

import collections

import networkx
try:
    import matplotlib.pyplot as plt
except ImportError:
    print('Matlotlib is not installed, '
          'drawing graphs will not work')
try:
    import pydot
except ImportError:
    print('Pydot is not installed, '
          'writing graphs to dot will not work')


class LogicFormGraph:
    """ Graph representation of a logical form. """

    def __init__(self, logic_form: str):
        self.logic_form = logic_form
        self.graph = logic_form_to_graph(logic_form)

    def __repr__(self):
        return (f'logic_form: {self.logic_form}\n'
                f'graph:\n'
                f' nodes: {self.graph.nodes(data=True)}\n'
                f' edges: {self.graph.edges()}')

    def is_binary_tree(self) -> bool:
        """ Check if graph is a binary tree. """
        if networkx.is_tree(self.graph) and \
           all(x[1] < 3 for x in self.graph.out_degree()):
            return True
        return False

    def list_preorder_nodes(self) -> list:
        """ Get a list of nodes following a preorder traversal. """
        return list(networkx.dfs_preorder_nodes(self.graph))

    def list_postorder_nodes(self) -> list:
        """ Get a list of nodes following a postorder traversal. """
        return list(networkx.dfs_postorder_nodes(self.graph))

    def draw(self, filename: str):
        """ Draw graph using Matplotlib. """
        pos = networkx.drawing.nx_agraph.graphviz_layout(self.graph)
        networkx.draw(self.graph)
        networkx.draw_networkx_labels(self.graph, pos)
        plt.savefig(filename, dpi=200)

    def write_gexf(self, filename: str):
        """ Export graph as GEXF file. """
        networkx.write_gexf(self.graph, filename)

    def write_dot(self, filename: str):
        """ Export graph as DOT file.

        To convert it to PDF:
        $ dot -Tpdf <filename> -o <pdf_file>

        """
        networkx.drawing.nx_pydot.write_dot(self.graph, filename)


def logic_form_to_graph(logic_form: str):
    """ Parse logic_form to networkx graph.

    Parameter:
    logic_form (str): a logical form of a logic_form

    Returns:
    graph (networkx.DiGraph)

    """
    # preprocess logic_form
    preproc_logic_form = (logic_form
                          .replace('[', '')
                          .replace(']', '')
                          .replace('"', '')
                          .replace('\'@', '(\'@')
                          .replace('(', ' ( ')
                          .replace(')', ' ) ')
                          .replace(',', ' '))
    tokens = preproc_logic_form.split()

    # extract topology
    topo = collections.defaultdict(list)
    parents = ['.']  # add artificial root
    for i, token in enumerate(tokens):
        token_id = f'{token}{i}'
        try:
            parent = parents[-1]
            if '@' in token:
                if tokens[i-1] == '(':
                    topo[parent].append(token_id)
                    parents.append(token_id)
            elif token == ')':
                parents.pop()
            elif token not in "()":
                topo[parent].append(token_id)
        except IndexError:
            raise SyntaxError("Invalid Logical Form")
    del topo['.']  # remove artificial root

    def __convert_tokenid_to_token(tokenid: str) -> str:
        return tokenid.rstrip('0123456789').replace("'", "")

    # construct graph
    graph = networkx.DiGraph()
    for inter_node, leaves in topo.items():
        token = __convert_tokenid_to_token(inter_node)
        graph.add_node(inter_node, predicate=token)
        for leaf in leaves:
            token = __convert_tokenid_to_token(leaf)
            graph.add_node(leaf, predicate=token)
            graph.add_edge(inter_node, leaf)

    if networkx.is_empty(graph):
        raise SyntaxError("Invalid Logical Form")

    return graph


def create_logic_form_graphs_from_logic_forms(logic_forms: list):
    """ Convert sentences to a logic forms

    Parameter:
    logic_forms (list): logic forms from CCG tool

    Returns:
    list of dicts with id (int) and a graph (LogicalFormGraph)
    for each sentence

    """
    return [{'id': i, 'graph': LogicFormGraph(sent)}
            for i, sent in enumerate(logic_forms)]
