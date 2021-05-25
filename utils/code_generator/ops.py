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

import ast

from check_type import is_variable, is_const_num, is_function_call
from connect_metadata_system import get_proto_fields

# Suppress pylint unused arguments warning:
# The __do_op* functions require to have 'env' arguments
# that might be unused for some operators.
# pylint: disable=unused-argument

def __join_params(params: list, sep='; ') -> str:
    """ Join non-empty parameters.

    Parameter:
    params (list): parameters to join
    sep (str): separator

    Returns:
    string of parameters joined by separator

    """
    return sep.join((param for param in params if param))


def __do_op_action(params: list, env=None) -> str:
    action = params[0].lower()
    args = params[1:]
    if 'compute' in action:
        func = args[0].replace("'", "")
        fargs = __join_params(args[1:], ', ')
        return f'compute_{func}({fargs})'
    if 'reverse' in action:
        fargs = __join_params([arg.replace(';', ',')
                               for arg in args],
                              sep=', ')
        return f'reverse({fargs})'
    if 'discard' in action:
        fargs = __join_params(args)
        return f'drop({fargs})'
    if 'stop' in action:
        fargs = __join_params(args)
        return f'stop({fargs})'
    if 'update' in action:
        fargs = __join_params(args)
        return f'update({fargs})'
    if any(a in action for a in ('form', 'match', 'help', 'aid')):
        # Assuming this generates no code
        return __join_params(args[1:])
    raise SyntaxError(f'Unknown action "{action}"')


def __do_op_and(params: list, env=None) -> str:
    same_mode = ('symmetric_mode', 'client_mode')
    first, second = params[0], params[1]
    if same_mode[0] in first and same_mode[1] in second:
        return __join_params(params, sep="&&")
    if '//' in second:
        return params[0]
    # Assuming this generates no code
    return __join_params(params)


def __do_op_associate(params: list, env=None) -> str:
    lhs, rhs = params[0], params[1]
    variable, value = lhs, rhs
    # convert to number and check order
    if is_const_num(rhs):
        value = ast.literal_eval(rhs)
    if is_const_num(lhs):
        variable, value = rhs, ast.literal_eval(lhs)
    params[0] = variable
    try:
        fieldname = env['field']
        params[1] = f'{fieldname}_value'
    except (KeyError, IndexError):
        params[1] = 'field_value'
    return __do_op_is(params, env)


def __do_op_changeto(params: list, env=None) -> str:
    return __do_op_is(params, env)


def __do_op_condition(params: list, env=None) -> str:
    if_block = 'if ({}) {{\n {};}}\n'
    cond = params[0].replace("; ", " && ")
    cond = cond.replace(" =", " ==")
    for param in params:
        if '@' in param:
            if_block = '/* if ({}) {{\n {};}}\n */'
    return if_block.format(cond, ';'.join(params[1:]))


def __do_op_in(params: list, env=None) -> str:
    lhs, rhs = params[0], params[1]
    return f'{rhs}.{lhs}'


def __do_op_in0(params: list, env=None) -> str:
    # Assuming this generates no code
    return __join_params(params)


def __do_op_is(params: list, env=None) -> str:
    lhs, rhs = params[0], params[1]
    variable, value = lhs, rhs

    # convert to number and check order
    if is_const_num(rhs):
        value = ast.literal_eval(rhs)
    if is_const_num(lhs):
        variable, value = rhs, ast.literal_eval(lhs)

    # if 'variable' is not a variable, use field name from env
    if not any((is_variable(x) for x in (variable, value))):
        try:
            if '{ENV_message}' not in env["message"]:
                proto_fields = get_proto_fields()
                field_names = [p[0] for p in proto_fields[env["protocol"]]]
                if env["field"] in field_names:
                    msg = env["message"].replace(' ', '_')
                    field = env["field"].replace(' ', '_')
                    variable = f'{msg}_hdr.{field}'
        except KeyError:
            # raise SyntaxError(f'No variable in @Is({variable},{value})')
            pass

    # fix order if necessary
    #if not is_variable(variable) and not is_const_num(value) and 'null' not in value:
    #    variable, value = value, variable

    if "||" in value:
        items = value.split("||")
        final = '({variable} = {items[0]})'
        for item in items:
            final = final+ " || ({variable} = {item})"
        return final

    return f'{variable} = {value}'


def __do_op_of(params: list, env=None) -> str:
    member, struct = params[0], params[1]
    if 'byte' in member:
        items = member.split('_bytes')
        byte_value = items[0]
        return f'extract({struct}, {byte_value})'
    if 'gateway_address' in member:
        return f'find_gateway({struct})'
    if 'OnesSum' in member:
        return f'ones_complement_sum((const void*){struct}, length)'
    if 'Ones' in member:
        return f'u16bit_ones_complement({struct})'
    if 'group_address' in member:
        return f'find_group_addr({struct})'
    if 'length' in member:
        return f'compute_length({struct})'
    if 'value' in member:
        return f'{struct}'
    return f'{struct}.{member}'


def __do_op_purpose(params: list, env=None) -> str:
    # Assuming this generates no code
    return __join_params(params)


def __do_op_purpose0(params: list, env=None) -> str:
    # Assuming this generates no code
    return __join_params(params)


def __do_op_startswith(params: list, env=None) -> str:
    if 'checksum' in params[0]:
        fargs = __join_params(params[1:], ', ')
        return f'compute_checksum({fargs})'
    return f'@StartsWith({__join_params(params, ",")})'


def __do_op_operateto(params: list, env=None) -> str:
    caller, callee = params[1], params[0]
    return f'// {caller} handle(s) {callee}'


def __do_op_pad(params: list, env=None) -> str:
    arg, pad_len = params[0], params[1]
    if 'zeros' in pad_len:
        fill_val = 0
    elif 'ones' in pad_len:
        fill_val = 1
    else:
        fill_val = 0
    if 'one_octet' in pad_len:
        pad_len = 1
    if is_variable(arg) or is_function_call(arg):
        pad = f'pad({arg}, sizeof({arg}), {fill_val}, {pad_len})'
        length = f'length += {pad_len}'
        return ';'.join((pad, length))
    return __join_params(params)


def __do_op_odd(params: list, env=None) -> str:
    arg = params[0]
    if is_const_num(arg):
        arg_num = ast.literal_eval(arg)
        return str(arg_num % 2 == 0).lower()
    if is_variable(arg) or is_function_call(arg):
        return f'isodd({arg})'
    try:
        if '{ENV_message}' not in env["message"]:
            proto_fields = get_proto_fields()
            field_names = [p[0] for p in proto_fields[env["protocol"]]]
            if env["field"] in field_names:
                msg = env["message"].replace(' ', '_')
                var = f'{msg}_hdr.{env["field"]}'
                return f'isodd({var})'
        return f'isodd({arg})'
    except KeyError:
        return f'isodd({arg})'


def __do_op_suggestuse(params: list, env=None) -> str:
    # TODO: register info to env dict?
    return f'@SuggestUse({__join_params(params, ",")})'


def __do_op_advcomment(params: list, env=None) -> str:
    return f'// {__join_params(params, ",")}'


def __do_op_advbefore(params: list, env=None) -> str:
    # register advice in MDS
    env['advice'] = True
    # add advice to code only
    advice = params[1]
    return f'{advice};'


def __do_op_use(params: list, env=None) -> str:
    role, field = params[0], params[1]
    return f'{field};\n/* {role} use {field} */ \n'


def __do_op_positionat(params: list, env=None) ->str:
    identity, position = params[0], params[1]
    return f'{identity};\n/* {identity} is at (a/an/the) {position} */ \n'


def __do_op_copy(params: list, env=None) -> str:
    caller, callee = params[0], params[1]
    if 'extract' in callee:
        items = callee.split(',')
        variable = items[0].split('(')[1]
        byte_value = items[1].split(')')[0]
        callee = ','.join([variable, byte_value])
    return f'copy(&{caller},(char*){callee})'

def __do_op_zero(params: list, env=None) -> str:
    num = "'0'"
    params.append(num)
    print("params:", params)
    return __do_op_is(params, env)

def __do_op_when(params: list, env=None) -> str:
    role = params[0]
    action = params[1]
    if '>=' in role:
        return __do_op_condition(params, env)
    return f'\n/*{role}*/\n {action}'

def __do_op_compound(params: list, env=None) -> str:
    return f'{__join_params(params, "_")}'

def __do_op_ignore(params: list, env=None) -> str:
    return 'dummy_action()'

def __do_op_zero(params: list, env=None) -> str:
    num = "'0'"
    params.append(num)
    return __do_op_is(params, env)


def __do_op_when(params: list, env=None) -> str:
    role = params[0]
    action = params[1]
    if '>=' in role:
        return __do_op_condition(params, env)
    return '\n/*{}*/\n {}'.format(role, action)


def __do_op_compound(params: list, env=None) -> str:
    return f'{__join_params(params, "_")}'


def __do_op_ignore(params: list, env=None) -> str:
    return 'dummy_action()'

def __do_op_comment(params: list, env=None) -> str:
    return f'// {__join_params(params, " ")}'

def __do_op_pseudo(params: list, env=None) -> str:
    variable = params[0]
    value = __join_params(params[1:], ' ')
    return f'{variable} = {value}'

def __do_op_length(params: list, env=None) -> str:
    sub = params[0]
    return f'{sub}.length'

def __do_op_add(params: list, env=None) -> str:
    left = params[0]
    right = params[1]
    return f'{left}+{right}'

def __do_op_reach(params: list, env=None) -> str:
    left, right = params[0], params[1]
    return f'{left} >= {right}'

def __do_op_call(params: list, env=None) -> str:
    mode, procedure = params[0], params[1]
    if 'passive' in mode:
        return f'{procedure}()'
    return ''

def __do_op_logicnot(params: list, env=None) -> str:
    var, val = params[0], params[1]
    if '||' in params[1]:
        items = val.split("||")
        final = f'({var} != {items[0]})'
        for item in items[1:]:
            final = final+ f' || ({var} != {item})'
        return final
    return f'{var} != {val}'

def __do_op_lessthan(params: list, env=None) -> str:
    var, val = params[0], params[1]
    return f'{var} <= {val}'

def __do_op_greaterthan(params: list, env=None) -> str:
    var, val = params[0], params[1]
    return f'{var} >= {val}'

def __do_op_select(params: list, env=None) -> str:
    arg, var = params[0], params[1]
    return f'{var} = select({arg})'

def __do_op_xor(params: list, env=None) -> str:
    arg1, arg2 = params[0], params[1]
    return f'{arg1}^{arg2}'

def __do_op_or(params: list, env=None) -> str:
    #arg1, arg2 = params[0], params[1]
    return __join_params(params, sep=" || ")

def __do_op_send(params: list, env=None) -> str:
    sender, content = params[0], params[1]
    if 'local_system' in sender:
        return f'send({content})'
    return f'// {sender}.send({content});\n'

def __do_op_transmit(params: list, env=None) -> str:
    return f'// {__join_params(params, " ")}'

def __do_op_with(params: list, env=None) -> str:
    former, latter = params[0], params[1]
    return f'{latter};\n {former}'

OPS = {
    "'@Action'": __do_op_action,
    "'@And'": __do_op_and,
    "'@Associate'": __do_op_associate,
    "'@ChangeTo'": __do_op_changeto,
    "'@Condition'": __do_op_condition,
    "'@In'": __do_op_in,
    "'@In0'": __do_op_in0,
    "'@Is'": __do_op_is,
    "'@Of'": __do_op_of,
    "'@Purpose'": __do_op_purpose,
    "'@Purpose0'": __do_op_purpose0,
    "'@StartsWith'": __do_op_startswith,
    "'@Pad'": __do_op_pad,
    "'@Odd'": __do_op_odd,
    "'@SuggestUse'": __do_op_suggestuse,
    "'@AdvComment'": __do_op_advcomment,
    "'@AdvBefore'": __do_op_advbefore,
    "'@OperateTo'": __do_op_operateto,
    "'@Use'": __do_op_use,
    "'@PositionAt'": __do_op_positionat,
    "'@Copy'": __do_op_copy,
    "'@Zeros'": __do_op_zero,
    "'@When'": __do_op_when,
    "'@Compound'": __do_op_compound,
    "'@Ignore'": __do_op_ignore,
    "'@Pseudo'": __do_op_pseudo,
    "'@Comment'": __do_op_comment,
    "'@Length'": __do_op_length,
    "'@Add'": __do_op_add,
    "'@Reach'": __do_op_reach,
    "'@Call'": __do_op_call,
    "'@LogicNot'": __do_op_logicnot,
    "'@LessThan'": __do_op_lessthan,
    "'@GreaterThan'": __do_op_greaterthan,
    "'@Select'": __do_op_select,
    "'@XOR'": __do_op_xor,
    "'@LogicNot0'": __do_op_logicnot,
    "'@Or'": __do_op_or,
    "'@Send'":__do_op_send,
    "'@Transmit'":__do_op_transmit,
    "'@With'": __do_op_with,
}
