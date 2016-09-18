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

import operator
import unittest

from sordid.modl import check


class CheckTestCase(unittest.TestCase):

    def test_repr(self):
        class SubClass(check.Check):
            def __str__(self):
                return 'a-string'
        self.assertEqual('a-string', repr(SubClass()))

    def test_str(self):
        self.assertEqual('Check()', str(check.Check()))
        class SubClass(check.Check):
            pass
        self.assertEqual('SubClass()', str(SubClass()))

    def test_check(self):
        instance = check.Check()
        with self.assertRaises(NotImplementedError):
            instance.check(1)
        class SubClass(check.Check):
            def check(self, instance):
                return 'a-check:' + str(instance)
        self.assertEqual('a-check:1', SubClass().check(1))


class BinopOperatorTestBase:

    @property
    def fn(self):
        return self.OP._OP

    def test_self_check(self):
        instance = check.Check()
        other = check.Check()
        result = self.fn(instance, other)
        self.assertIsInstance(result, self.OP)
        lval, rval = result.checks
        self.assertIs(instance, lval)
        self.assertIs(other, rval)

    def test_self_object(self):
        instance = check.Check()
        other = object()
        result = self.fn(instance, other)
        self.assertIsInstance(result, self.OP)
        lval, rval = result.checks
        self.assertIs(instance, lval)
        self.assertIsInstance(rval, check.K)
        self.assertIs(other, rval.val)

    def test_other_self(self):
        instance = check.Check()
        other = object()
        result = self.fn(other, instance)
        self.assertIsInstance(result, self.OP)
        lval, rval = result.checks
        self.assertIsInstance(lval, check.K)
        self.assertIs(other, lval.val)
        self.assertIs(instance, rval)


class KTestCase(unittest.TestCase):

    def test_value(self):
        self.assertEqual(1, check.K(1).val)
        self.assertEqual(None, check.K(None).val)
        self.assertEqual(operator.add, check.K(operator.add).val)
        k = check.K(10)
        self.assertIs(k, check.K(k).val)

    def test_check(self):
        o = object()
        self.assertIs(o, check.K(o).check(int, 1))

    def test_str(self):
        self.assertEqual('K(1)', str(check.K(1)))
        self.assertEqual('K(\'val\')', str(check.K('val')))


class CompoundCheckTestCase(unittest.TestCase):

    def test_checks(self):
        k1 = check.K(1)
        k2 = check.K(3)
        k3 = check.K(4)
        compound = check.CompoundCheck(k1, k2, k3)
        actual1, actual2, actual3 = compound.checks
        self.assertIs(k1, actual1)
        self.assertIs(k2, actual2)
        self.assertIs(k3, actual3)

    def test_not_enough_args(self):
        for args in ((), (check.K(1),)):
            with self.assertRaisesRegex(TypeError, 'Compound check requires at least 2 checks'):
                check.CompoundCheck(*args)

    def test_not_check(self):
        o1 = object()
        o2 = object()
        lval, rval = check.CompoundCheck(o1, o2).checks
        self.assertIsInstance(lval, check.K)
        self.assertIs(o1, lval.val)
        self.assertIsInstance(rval, check.K)
        self.assertIs(o2, rval.val)


class FlattenableCompoundCheckTestCase(unittest.TestCase):

    def test_make_val_val(self):
        val_lval = check.Check()
        val_rval = check.Check()
        instance = check.FlattenableCompoundCheck.make(val_lval, val_rval)
        lval, rval = instance.checks
        self.assertIs(val_lval, lval)
        self.assertIs(val_rval, rval)

    def test_make_same_val(self):
        c1 = check.Check()
        c2 = check.Check()
        val_lval = check.FlattenableCompoundCheck(c1, c2)
        val_rval = check.Check()
        instance = check.FlattenableCompoundCheck.make(val_lval, val_rval)
        v1, v2, v3 = instance.checks
        self.assertIs(c1, v1)
        self.assertIs(c2, v2)
        self.assertIs(val_rval, v3)

    def test_make_val_same(self):
        val_lval = check.Check()
        c1 = check.Check()
        c2 = check.Check()
        val_rval = check.FlattenableCompoundCheck(c1, c2)
        instance = check.FlattenableCompoundCheck.make(val_lval, val_rval)
        v1, v2, v3 = instance.checks
        self.assertIs(val_lval, v1)
        self.assertIs(c1, v2)
        self.assertIs(c2, v3)

    def test_make_val_same(self):
        c1 = check.Check()
        c2 = check.Check()
        val_lval = check.FlattenableCompoundCheck(c1, c2)
        c3 = check.Check()
        c4 = check.Check()
        val_rval = check.FlattenableCompoundCheck(c3, c4)
        instance = check.FlattenableCompoundCheck.make(val_lval, val_rval)
        v1, v2, v3, v4 = instance.checks
        self.assertIs(c1, v1)
        self.assertIs(c2, v2)
        self.assertIs(c3, v3)
        self.assertIs(c4, v4)



class InfixCheckTestCase(unittest.TestCase):

    def test_str(self):
        self.assertEqual('(K(1) ? K(2))', str(check.InfixCheck(1, 2)))


class AccumulatorCheck(InfixCheckTestCase):

    def test_accumulate(self):
        class GetV(check.Check):

            def __init__(self, index):
                super(GetV, self).__init__()
                self.index = index

            def check(self, instance):
                return instance[self.index]

            def __str__(self):
                return 'GetV({})'.format(self.index)

        accumulator = GetV(0) + GetV(1) + GetV(2) + GetV(3) + GetV(4)
        self.assertEqual(35, accumulator.check([1, 3, 7 ,11, 13]))


class NonFlattenableBinopOperatorTestCase(BinopOperatorTestBase):

    def test_self_same(self):
        instance = check.Check()
        other_lval = check.Check()
        other_rval = check.Check()
        other = self.fn(other_lval, other_rval)
        result = self.fn(instance, other)
        self.assertIsInstance(result, self.OP)
        val1, val2 = result.checks
        self.assertIs(instance, val1)
        self.assertIs(other, val2)

    def test_same_self(self):
        instance = check.Check()
        other_lval = check.Check()
        other_rval = check.Check()
        other = self.fn(other_lval, other_rval)
        result = self.fn(other, instance)
        self.assertIsInstance(result, self.OP)
        val1, val2 = result.checks
        self.assertIs(other, val1)
        self.assertIs(instance, val2)


class FlattenableBinopOperatorTestCase(BinopOperatorTestBase):

    def test_self_same(self):
        instance = check.Check()
        other_lval = check.Check()
        other_rval = check.Check()
        other = self.fn(other_lval, other_rval)
        result = self.fn(other, instance)
        self.assertIsInstance(result, self.OP)
        val1, val2, val3 = result.checks
        self.assertIs(other_lval, val1)
        self.assertIs(other_rval, val2)
        self.assertIs(instance, val3)

    def test_same_same(self):
        instance_lval = check.Check()
        instance_rval = check.Check()
        other_lval = check.Check()
        other_rval = check.Check()
        instance = self.fn(instance_lval, instance_rval)
        other = self.fn(other_lval, other_rval)
        result = self.fn(instance, other)
        self.assertIsInstance(result, self.OP)
        val1, val2, val3, val4 = result.checks
        self.assertIs(instance_lval, val1)
        self.assertIs(instance_rval, val2)
        self.assertIs(other_lval, val3)
        self.assertIs(other_rval, val4)


_OPERATORS = [
    check.And,
    check.Or,
    check.Add,
    check.Sub,
]

for _op in _OPERATORS:
    _test_name = '{}TestCase'.format(_op.__name__)
    if issubclass(_op, check.FlattenableCompoundCheck):
        _base = FlattenableBinopOperatorTestCase
    else:
        _base = NonFlattenableBinopOperatorTestCase
    globals()[_test_name] = type(_test_name,
                                 (_base, unittest.TestCase),
                                 {'OP': _op})


if __name__ == '__main__':
    unittest.main()
