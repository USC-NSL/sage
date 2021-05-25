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


def __prepare_data(data: str) -> str:
    return data.replace("'", "")


def is_predicate(data: str) -> bool:
    """ Returns true if predicate is a logical form predicate. """
    return '@' in data


def is_variable(data: str) -> bool:
    """ Returns true if predicate is a variable.

    Note: requires to start all variables with a capital letter.

    """
    return data[0].isupper()


def is_function_call(data: str) -> bool:
    """ Returns true if predicate is probably a function call.  """
    return all(bracket in data for bracket in ('(', ')'))


def is_const_num(data: str) -> bool:
    """ Returns true if predicate is a number. """
    return __prepare_data(data).isnumeric()


def is_const_str(data: str) -> bool:
    """ Returns true if predicate is a constant string.

    Note: requires to start all constant string with a lower case
    letter.

    """
    return __prepare_data(data)[0].islower() and not '@' in data
