# Copyright 2016 Rafe Kaplan
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""
Library used for defining invariant checks on classes.
"""

import operator


class Check:
    """Base class for all invariant checks."""

    def __repr__(self):
        return str(self)

    def __str__(self):
        return '{}()'.format(type(self).__name__)

    def check(self, instance):
        """Call check for class on instance.

        Subclasses must override this method.

        Args:
            instance: Instance to perform check on.

        Returns:
            Value of check.
        """
        raise NotImplementedError

    def __and__(self, other):
        return And.make(self, other)

    def __rand__(self, other):
        return And.make(other, self)

    def __or__(self, other):
        return Or.make(self, other)

    def __ror__(self, other):
        return Or.make(other, self)

    def __add__(self, other):
        return Add.make(self, other)

    def __radd__(self, other):
        return Add.make(other, self)

    def __sub__(self, other):
        return Sub(self, other)

    def __rsub__(self, other):
        return Sub(other, self)


class K(Check):

    @property
    def val(self):
        return self.__val

    def __init__(self, value):
        self.__val = value

    def check(self, cls, instance):
        return self.__val

    def __str__(self):
        return 'K({!r})'.format(self.__val)


class CompoundCheck(Check):

    @property
    def checks(self):
        return self.__checks

    def __init__(self, *args):
        if len(args) < 2:
            raise TypeError('Compound check requires at least 2 checks')

        args = tuple((c if isinstance(c, Check) else K(c)) for c in args)
        self.__checks = args


class FlattenableCompoundCheck(CompoundCheck):

    @classmethod
    def make(cls, lval, rval):
        args = []
        if isinstance(lval, cls):
            args.extend(lval.checks)
        else:
            args.append(lval)
        if isinstance(rval, cls):
            args.extend(rval.checks)
        else:
            args.append(rval)
        return cls(*args)


class InfixCheck(CompoundCheck):

    _SYMBOL = ' ? '

    def __str__(self):
        checks = self._SYMBOL.join(str(check) for check in self.checks)
        return '(' + checks + ')'


class AccumulatorCheck(InfixCheck):

    def check(self, instance):
        checks = self.checks
        result = checks[0].check(instance)
        op = self._OP
        for next in checks[1:]:
            result = op(result, next.check(instance))
        return result


class And(FlattenableCompoundCheck, AccumulatorCheck):

    _SYMBOL = ' & '
    _OP = operator.and_


class Or(FlattenableCompoundCheck, AccumulatorCheck):

    _SYMBOL = ' | '
    _OP = operator.or_


class Add(FlattenableCompoundCheck, AccumulatorCheck):
    _SYMBOL = ' + '
    _OP = operator.add


class Sub(AccumulatorCheck):
    _SYMBOL = ' - '
    _OP = operator.sub
