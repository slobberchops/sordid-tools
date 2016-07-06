#!/usr/bin/env python
#
# Copyright 2012 Rafe Kaplan
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#

import operator

import unittest

import mox

from sordid import proputils
from sordid import proputils_test
from sordid import propval


class ValidatorTest(mox.MoxTestBase):

  def testBasicValidator(self):
    val_func = self.mox.CreateMockAnything()
    val = propval.Validator(val_func)

    val_func(1).AndReturn(False)
    val_func(2).AndReturn(True)

    self.mox.ReplayAll()

    self.assertFalse(val(1))
    self.assertTrue(val(2))

  def testAnd(self):
    val_func1 = self.mox.CreateMockAnything()
    val_func2 = self.mox.CreateMockAnything()

    val1 = propval.Validator(val_func1)
    val2 = propval.Validator(val_func2)

    and_val = val1 & val2

    val_func1(1).AndReturn(False)

    val_func1(2).AndReturn(True)
    val_func2(2).AndReturn(False)

    val_func1(3).AndReturn(True)
    val_func2(3).AndReturn(True)

    self.mox.ReplayAll()

    self.assertFalse(and_val(1))
    self.assertFalse(and_val(2))
    self.assertTrue(and_val(3))

  def testOr(self):
    val_func1 = self.mox.CreateMockAnything()
    val_func2 = self.mox.CreateMockAnything()

    val1 = propval.Validator(val_func1)
    val2 = propval.Validator(val_func2)

    or_val = val1 | val2

    val_func1(1).AndReturn(False)
    val_func2(1).AndReturn(False)

    val_func1(2).AndReturn(True)

    val_func1(3).AndReturn(False)
    val_func2(3).AndReturn(True)

    self.mox.ReplayAll()

    self.assertFalse(or_val(1))
    self.assertTrue(or_val(2))
    self.assertTrue(or_val(3))

  def testNot(self):
    val_func = self.mox.CreateMockAnything()

    val = ~propval.Validator(val_func)

    val_func(1).AndReturn(False)
    val_func(2).AndReturn(True)

    self.mox.ReplayAll()

    self.assertTrue(val(1))
    self.assertFalse(val(2))

  def testFuncValidatorOperators(self):
    val_func1 = self.mox.CreateMockAnything()
    val_func2 = self.mox.CreateMockAnything()

    val = propval.Validator(val_func1)

    or_val = val | val_func2

    val_func1(1).AndReturn(False)
    val_func2(1).AndReturn(False)

    val_func1(2).AndReturn(True)

    val_func1(3).AndReturn(False)
    val_func2(3).AndReturn(True)

    self.mox.ReplayAll()

    self.assertFalse(or_val(1))
    self.assertTrue(or_val(2))
    self.assertTrue(or_val(3))


class ConstantsTest(unittest.TestCase):

  def testNone(self):
    self.assertTrue(propval.NONE(None))
    self.assertFalse(propval.NONE(1))
    self.assertFalse(propval.NONE(0))
    self.assertFalse(propval.NONE(''))
    self.assertFalse(propval.NONE('str'))
    self.assertFalse(propval.NONE([]))

  def testEmpty(self):
    self.assertTrue(propval.EMPTY(None))
    self.assertFalse(propval.EMPTY(1))
    self.assertTrue(propval.EMPTY(0))
    self.assertTrue(propval.EMPTY(''))
    self.assertFalse(propval.EMPTY('str'))
    self.assertTrue(propval.EMPTY([]))
    self.assertFalse(propval.EMPTY([1]))


class ValidatorDefTest(unittest.TestCase):

  def testValidatorDef(self):
    @propval.validator_def
    def gt_val(number):
      def gt(value):
        return value > number
      return gt

    more_than_7 = gt_val(7)

    self.assertFalse(more_than_7(7))
    self.assertTrue(more_than_7(8))

    @propval.validator_def
    def lt_val(number):
      def lt(value):
        return value < number
      return lt

    not_between_2_and_8 = more_than_7 | lt_val(3)

    self.assertTrue(not_between_2_and_8(2))
    self.assertFalse(not_between_2_and_8(3))
    self.assertFalse(not_between_2_and_8(7))
    self.assertTrue(not_between_2_and_8(8))


class ValidatedPropertyTest(proputils_test.PropertyTestMixin,
                            unittest.TestCase):

  def new_class(self):
    class C(object):
      @propval.ValidatedProperty
      def p(value):
        return bool(value)
    return C

  def testFailValidation(self):
    c = self.C()
    proputils.config_props(self.C)
    self.assertRaises(ValueError, setattr, c, 'p', False)


class StrictPropertyTest(proputils_test.PropertyTestMixin,
                         unittest.TestCase):

  def new_class(self):
    class C(object):
      p = propval.StrictProperty(str)
      i = propval.StrictProperty(int)
      s = propval.StrictProperty(basestring)
    return C

  def testInitialState_Set(self):
    c = self.C()
    self.assertRaises(TypeError, setattr, c, 'p', 1)

  def testAssignWrongType(self):
    c = self.C()
    proputils.config_props(self.C)

    # Nones are not an exception
    self.assertRaises(TypeError, setattr, c, 'p', None)
    self.assertRaises(TypeError, setattr, c, 'i', None)
    self.assertRaises(TypeError, setattr, c, 's', None)

    # Must assign str
    self.assertRaises(TypeError, setattr, c, 'p', u'unicode')
    self.assertRaises(TypeError, setattr, c, 'p', 1.2)
    self.assertRaises(TypeError, setattr, c, 'p', 1)

    # Must assign int
    self.assertRaises(TypeError, setattr, c, 'i', 'str')
    self.assertRaises(TypeError, setattr, c, 'i', 1.2)
    self.assertRaises(TypeError, setattr, c, 'i', long(1))

    # Must assign any string
    self.assertRaises(TypeError, setattr, c, 's', 1.2)
    self.assertRaises(TypeError, setattr, c, 's', long(1))

  def testAssignRightTypes(self):
    c = self.C()
    proputils.config_props(self.C)

    c.p = 'a string'
    self.assertEquals('a string', c.p)
    c.p = 'another string'
    self.assertEquals('another string', c.p)

    c.i = 10
    self.assertEquals(10, c.i)
    c.i = 20
    self.assertEquals(20, c.i)

    c.s = 'a str'
    self.assertEquals('a str', c.s)
    c.s = u'a unicode'
    self.assertEquals('a unicode', c.s)
    c.s = 'another str'
    self.assertEquals('another str', c.s)
    c.s = u'another unicode'
    self.assertEquals('another unicode', c.s)


class CmpTest(unittest.TestCase):

    def testBinop(self):
        validator = propval.CMP(operator.gt, 10)
        self.assertFalse(validator(10))
        self.assertTrue(validator(11))

    def testLt(self):
        validator = propval.CMP < 10
        self.assertFalse(validator(10))
        self.assertTrue(validator(9))

    def testLe(self):
        validator = propval.CMP <= 10
        self.assertFalse(validator(11))
        self.assertTrue(validator(10))

    def testGt(self):
        validator = propval.CMP > 10
        self.assertFalse(validator(10))
        self.assertTrue(validator(11))

    def testGe(self):
        validator = propval.CMP >= 10
        self.assertFalse(validator(9))
        self.assertTrue(validator(10))


class IsInTest(unittest.TestCase):

    def testIn(self):
        validator = propval.is_in([10, 20, 30])
        self.assertFalse(validator(11))
        self.assertTrue(validator(10))
        self.assertFalse(validator(21))
        self.assertTrue(validator(20))
        self.assertFalse(validator(31))
        self.assertTrue(validator(30))


if __name__ == '__main__':
  unittest.main()
