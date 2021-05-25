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

import logic_form_graph as lfg


# for each predicate: a list of tuples that contain the allowed
# predicate types of successors
# available predicate types: variable, const_num, const_str
predicate_rules = {
    '@Action': [
        ('const_str', 'const_str'), # '@Action'('form','reversed')
        ('variable', 'const_str'),  # '@Action'('Recompute','checksum')
    ],
    '@And': [  # avoid '@And'(SequenceNum,'0')
        ('const_str', 'const_str'),
        ('const_str', 'variable'),
        ('variable', 'const_str'),
        ('variable', 'variable'),
        ('const_num', 'const_num'),
    ],
    '@Associate': [
        ('variable', 'const_num'),  # '@Associate'(Code,'0')
        ('const_str', 'const_num'),  # '@ChangeTo'('type_code','0')
        ('const_str', 'const_str'),  # @Associate'('service_host','client_host')
    ],
    '@ChangeTo': [
        ('const_str', 'const_num'),  # @'ChangeTo'('type_code','0')
    ],
    '@Condition': [  # avoid @Condition('0', ...)
        ('const_str', 'const_str'),
        ('const_str', 'const_num'),
        ('const_str', 'variable'),
        ('variable', 'const_str'),
        ('variable', 'const_num'),
        ('variable', 'variable'),
    ],
    '@In': [],
    '@In0': [  # avoid @In0('123') and @In0(Octet)
        ('const_str',),
    ],
    '@Is': [
        ('variable', 'const_num'),  # '@Is'(SequenceNum,'0')
        ('variable', 'const_str'),  # '@Is'(y,'reversed')
        ('const_str', 'const_str'),  # '@Is'('padded','data')
        ('const_num', 'const_str'),  # '@Is'('8','echo_message')
        ('const_str', 'const_num'),  # '@Is'('checksum_field','0')
    ],
    '@Of': [
        ('variable', 'variable'),  # '@Of'(Address,Source)
        ('variable', 'const_str'),  # '@Of'(Destination,'echo_reply_message')
        ('const_str', 'variable'),  # '@Of'('16_bit_one's_complement',OnesSum)
        ('const_str', 'const_str'),  # '@Of'('echo_message','echo_reply_message')
        ('const_str', 'const_num'),  # '@Of'('nearest_power','2')
    ],
    '@Purpose': [],
    '@Purpose0': [],
    '@StartsWith': [],
    '@OperateTo': [
        # ('const_str', 'const_str'),
        # ('variable', 'variable'),
    ],
    '@PositionAt': [],
    '@Pad': [
        ('variable', 'const_num'),
        ('const_str', 'const_num'),
    ],
    '@Odd': [],
    '@SuggestUse': [],
    '@AdvComment': [],
    '@AdvBefore': [  # avoid @AdvBefore('0', ...)
        ('const_str', 'const_str'),
        ('const_str', 'const_num'),
        ('const_str', 'variable'),
        ('variable', 'const_str'),
        ('variable', 'const_num'),
        ('variable', 'variable'),
    ],
    '@Compound': [],
    '@When': [],
    '@Ignore': [],
    '@Identify': [],
    '@Zeros': [],
    '@Indicate':[],
    '@InsertedAt':[
        ('const_str', 'const_str'),
    ],
    '@Depart':[],
    '@Between':[],
    '@Pseudo':[
        ('const_str', 'const_str'),
    ],
    '@Comment':[
        ('const_str', 'const_str'),
    ],
    '@Length':[
        ('const_str'),
    ],
    '@Add':[
        ('const_str', 'const_str'),
    ],
    '@Reach':[
        ('const_str', 'const_str'),
        ('const_str', 'variable'),
        ('const_str', 'variable'),
        ('variable', 'variable'),
    ],
    '@Call':[
        ('const_str', 'const_str'),
        ('const_str', 'variable'),
    ],
    '@LogicNot':[],
    '@LessThan':[],
    '@GreaterThan':[],
    '@Or':[],
    '@XOR':[],
    '@LogicNot0':[],
    '@Transmit':[],
    '@Send':[],
    '@With':[],
    '@Select':[],
}


# for each predicate: a list of predicates that should not precede
# the given predicate in the graph
predicate_order_denylist = {
    '@Action': [],
    '@And': [
        '@Zeros',
    ],
    '@Associate': [],
    '@ChangeTo': [],
    '@Condition': [
        '@OperateTo',
        '@And',
        '@With',
        '@Or',
    ],
    '@In': [],
    '@In0': [],
    '@Is': [
        '@Of',
        '@Action',
        # '@OperateTo',
        '@Is',
    ],
    '@Of': [
        '@Compound',
    ],
    '@Purpose': [
        '@Purpose',
    ],
    '@Purpose0': [],
    '@StartsWith': [],
    '@OperateTo': [],
    '@Pad': [],
    '@Odd': [],
    '@SuggestUse': [],
    '@AdvComment': [],
    '@AdvBefore': [
        '@Condition',
        '@Action',
        '@When',
    ],
    '@When': [],
    '@Add':[
        '@Of',
    ],
    '@Ignore': [],
    '@Identify': [],
    '@Zeros': [],
    '@LogicNot': [],
    '@LessThan':[],
    '@GreaterThan':[],
    '@Or':[],
    '@XOR':[],
    '@LogicNot0':[
        '@OperateTo',
        '@Transmit',
    ],
    '@Transmit':[],
    '@Send':[],
    '@With':[
        '@And',
    ],
    '@Select':[],
}

# for each predicate: a sequence of predicates that should not be the
# successors of a given predicate in the graph. No successor predicate
# can be written as ''. For example, to filter out the logic form
# '@Is'('@And'('X', '0'),'0'), add ('@And', '') to '@Is'
predicate_sequence_denylist = {
    '@Action': [],
    '@And': [
        ('', '@LogicNot0'),
    ],
    '@Associate': [],
    '@ChangeTo': [],
    '@Condition': [
        ('@Pad', '@Odd'),
        ('@Is', '@Associate'),
        ('@Action', '@Associate'),
        ('@Action', '@Is'),
        ('@Action', '@LogicNot'),
        ('@Action', '@LessThan'),
        ('@Action', '@GreaterThan'),
        ('@Select', '@LogicNot'),
        ('@Action', '@And'),
        ('@Send', '@Or'),
    ],
    '@In': [
        ('@And', '@LogicNot0'),
    ],
    '@In0': [
        ('@LogicNot0',),
    ],
    '@Is': [
        ('@And', ''),
        ('', '@And'),
        ('', '@LogicNot0'),
        ('@LogicNot0', ''),
        ('@LogicNot0', '@And'),
        ('@And', '@LogicNot0'),
        # ('', '@In0'),
    ],
    '@Of': [],
    '@Purpose': [],
    '@Purpose0': [],
    '@StartsWith': [],
    '@OperateTo': [
        ('@And', ''),
        ('@Is', '@Of'),
    ],
    '@PositionAt': [],
    '@Pad': [],
    '@Odd': [],
    '@SuggestUse': [],
    '@AdvComment': [],
    '@AdvBefore': [],
    '@Compound':[],
    '@When': [],
    '@Ignore': [],
    '@Identify': [],
    '@Zeros': [],
    '@Indicate':[],
    '@InsertedAt':[],
    '@Depart':[],
    '@Between':[],
    '@Pseudo':[],
    '@Comment':[],
    '@Length':[],
    '@Add':[
        ('@Of',''),
    ],
    '@Reach':[],
    '@Call':[],
    '@LogicNot':[
        ('', '@And'),
        ('@And', ''),
    ],
    '@LessThan':[],
    '@GreaterThan':[],
    '@Or':[],
    '@XOR':[],
    '@LogicNot0':[
        ('', '@And'),
        ('@And', ''),
    ],
    '@Transmit':[
        ('@And', ''),
    ],
    '@Send':[],
    '@With':[],
    '@Select':[],
}


def __is_predicate(data: str) -> bool:
    """ Returns true if predicate is a logical form predicate. """
    return '@' in data


def __is_variable(data: str) -> bool:
    """ Returns true if predicate is a variable.

    Note: requires to start all variables with a capital letter.

    """
    return data[0].isupper()


def __is_const_num(data: str) -> bool:
    """ Returns true if predicate is a number. """
    return data.isnumeric()


def __is_const_str(data: str) -> bool:
    """ Returns true if predicate is a constant string.

    Note: supports constant strings starting with a lowercase letter
    or a number

    """
    # common case: string starts with a lowercase letter
    test_str = data[0].islower()
    # special case: string starts with a number. see '16_bit_one's_complement'
    test_num = data[0].isnumeric() and not data.isnumeric()
    return  (test_str or test_num) and not '@' in data


def _check_rules_node(graph, node: str) -> bool:
    """ Check predicate rules on a predicate graph node.

    Parameters:
    graph: graph attribute of LogicFormGraph object
    node (str): name of the node to check

    Returns:
    true if node conforms a predicate rule

    """
    node_predicate = graph.nodes[node]['predicate']
    for rules in predicate_rules[node_predicate]:
        check_results = []
        for rule, child in zip(rules, graph.successors(node)):
            child_predicate = graph.nodes[child]['predicate']
            if __is_predicate(child_predicate):
                check_results.append(True)
                continue
            try:
                check_func = globals()[f'__is_{rule}']
                check_results.append(check_func(child_predicate))
            except KeyError:
                text = f'Invalid predicate rule for {child_predicate}'
                raise ValueError(text)
        if check_results and all(check_results):
            return True
    if not predicate_rules[node_predicate]:
        return True
    return False


def check_pred_rules(lf_graph: dict) -> bool:
    """ Check predicate rules in logical form graph.

    Parameters:
    lf_graph: dict of id (int) and graph (LogicalFormGraph)

    Returns:
    true if logical form graph conforms predicate rules

    """
    graph = lf_graph['graph'].graph
    predicate_nodes = [g for g in graph.nodes()
                       if '@' in graph.nodes[g]['predicate']]
    return all(_check_rules_node(graph, node) for node in predicate_nodes)


def check_pred_order(lf_graph: dict) -> bool:
    """ Check predicate order in logical form graph.

    Parameters:
    lf_graph: dict of id (int) and graph (LogicalFormGraph)

    Returns:
    true if logical form graph conforms predicate order

    """
    graph = lf_graph['graph'].graph
    for node, node_data in graph.nodes(data=True):
        predicate = node_data['predicate']
        try:
            if any(g for g in graph.predecessors(node)
                   if graph.nodes[g]['predicate']
                   in predicate_order_denylist[predicate]):
                return False
        except KeyError:
            pass
    return True


def check_pred_sequence(lf_graph: dict) -> bool:
    """ Check predicate sequences in logical form graph. See
    documentation of predicate_sequence_denylist for details.

    Parameters:
    lf_graph: dict of id (int) and graph (LogicalFormGraph)

    Returns:
    true if logical form graph conforms predicate sequence

    """
    graph = lf_graph['graph'].graph
    predicate_nodes = [g for g in graph.nodes()
                       if '@' in graph.nodes[g]['predicate']]
    for node in predicate_nodes:
        child_preds = [graph.nodes[child]['predicate']
                       for child in graph.successors(node)]
        child_preds = tuple(map(lambda x: '' if '@' not in x else x,
                                child_preds))
        predicate = graph.nodes[node]['predicate']
        if child_preds in predicate_sequence_denylist[predicate]:
            return False
    return True


def __check_duplicate_args(lf_graph: dict) -> bool:
    """ Check for duplicated predicate arguments in logical form graph.

    Parameters:
    lf_graph: dict of id (int) and graph (LogicalFormGraph)

    Returns:
    true if logical form graph has no predicate w/ duplicate arguments

    """
    graph = lf_graph['graph'].graph
    predicate_nodes = [g for g in graph.nodes()
                       if '@' in graph.nodes[g]['predicate']]
    for node in predicate_nodes:
        child_predicates = [graph.nodes[child]['predicate']
                            for child in graph.successors(node)
                            if '@' not in graph.nodes[child]['predicate']]
        if len(child_predicates) > 1 and \
           all(x == child_predicates[0] for x in child_predicates):
            return False
    return True


def __check_duplicate_preds(lf_graph: dict) -> bool:
    """ Check for duplicated predicates in logical form graph.

    Parameters:
    lf_graph: dict of id (int) and graph (LogicalFormGraph)

    Returns:
    true if logical form graph has no duplicate predicates

    """
    nodes = lf_graph['graph'].list_preorder_nodes()
    predicates = []
    predicate = []
    for node in reversed(nodes):
        # remove tailing node id and add node to pred
        predicate.insert(0, node.rstrip("0123456789"))
        if '@' in node:
            # handle nested predicates
            if len(predicate) > 3:
                predicate.append(predicate[:3])
                break
            if len(predicate) != 3:
                tmp_idx = -1
                while len(predicate) != 3:
                    try:
                        predicate.append(predicates[tmp_idx])
                        tmp_idx -= 1
                    except IndexError:
                        # the predicate has only one argument
                        break
            # convert predicate to string and add to predicates
            predicates.append("".join(predicate))
            predicate = []
    # check for duplicates
    if len(predicates) != len(set(predicates)):
        return False
    return True


def check_pred_duplicates(lf_graph: dict) -> bool:
    """ Check for duplicated predicate arguments in logical form graph.

    Parameters:
    lf_graph: dict of id (int) and graph (LogicalFormGraph)

    Returns: true if logical form graph has no duplicate predicates
    and no predicate w/ duplicate arguments

    """
    return __check_duplicate_preds(lf_graph) and __check_duplicate_args(lf_graph)


def check_pred_all(lf_graphs: list, mode: str) -> list:
    """ Check predicates on a list of logical forms.
    Filter out nonconforming logical forms.

    Parameter:
    lf_graphs (list): logical forms
    mode (str): name of check mode, valid options: rules, order

    Returns:
    a list of logical forms that conform with the predicate orders
    from lf_graphs

    """
    try:
        check_func = globals()[f'check_pred_{mode}']
    except KeyError:
        raise ValueError(f'Invalid predicate checker mode: {mode}')
    return [lf for lf in lf_graphs if check_func(lf) is True]


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument(
        'logicforms',
        help='Logic forms to process',
        nargs='+', default=[],
    )
    parser.add_argument(
        '--check', '-c',
        help=('Checks to run, separated by ",".'
              'Available options are: order, rules, sequence, duplicates'),
        type=str, default='order,rules,sequence,duplicates',
    )
    parser.add_argument(
        '--quiet', '-q',
        help='Surpress verbose mode',
        action='store_true',
    )
    args = parser.parse_args()

    lfgraphs = lfg.create_logic_form_graphs_from_logic_forms(args.logicforms)

    for check_mode in args.check.split(','):
        if not args.quiet:
            print(f'Checking {check_mode}...')
        lfgraphs = check_pred_all(lfgraphs, mode=check_mode)

    if not args.quiet:
        for lfg in lfgraphs:
            print(f'{lfg["id"]}: {lfg["graph"].logic_form}')
