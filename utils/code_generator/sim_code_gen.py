#! /usr/bin/env python3

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

import importlib
from code_gen import *

UTILS_DIR = pathlib.Path(__file__).parent.absolute() / '..'
sys.path.insert(0, str(UTILS_DIR))
from similarity import similarity_map
import dyn_term

def add_var_lower():
    var_list = dyn_term.VARS
    with open("dyn_term.py", 'a') as fp:
        fp.write("VARS_CONVERSION = {\n")
        for var_ in var_list:
            fp.write("\t\'%s\':\'%s\',\n" % (var_.lower(), var_))
        fp.write("}\n")

def add_field_lower():
    field_list = dyn_term.FIELDS
    with open("dyn_term.py", 'a') as fp:
        fp.write("FIELDS_CONVERSION = {\n")
        for field_ in field_list:
            fp.write("\t\'%s_field\':\'hdr->%s\',\n" % (field_.lower(), field_))
        fp.write("\t\'hdr->hdr\':\'hdr\',\n")
        fp.write("}\n")


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument(
        'logicform',
        help='Logic form to process',
        type=str,
    )
    parser.add_argument(
        '--outfile', '-o',
        help='Write generated code to this file',
        type=str,
        default='state_code.txt',
    )
    args = parser.parse_args()
    prepreprocessed_lf = prepreprocess_logic_form(args.logicform, settings.ROLE_KEYWORDS)
    tokenized_lfs = parse_logic_form(prepreprocessed_lf)
    print(tokenized_lfs)
    filtered_lfs = filter_logic_forms(tokenized_lfs, settings.DENYLIST)
    eval_res = eval_logic_forms(filtered_lfs, None)
    res = postprocess_code("{};\n".format(';\n'.join(eval_res)), settings.CODE_CONVERSIONS)
    try:
        res = postprocess_code(res, dyn_term.VARS_CONVERSION)
    except:
        add_var_lower()
        var_ls = dyn_term.VARS
        var_map = dict()
        for var in var_ls:
            var_map[var.lower()] = var
        res = postprocess_code(res, var_map)

    try:
        res = postprocess_code(res, dyn_term.FIELDS_CONVERSION)
    except:
        add_field_lower()
        field_ls = dyn_term.FIELDS
        field_map = dict()
        for field in field_ls:
            field_map[f'{field.lower()}_field'] = f'hdr->{field}'
        field_map['hdr->hdr'] = 'hdr'
        res = postprocess_code(res, field_map)

    with open(args.outfile, 'a') as f:
        f.write(res)
        f.write("\n")
