#!/usr/bin/env python
#
# Copyright 2011 Rafe Kaplan
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

import unittest

from sordid import enum
from sordid import test_util


class Color(enum.Enum):

  RED = 1
  GREEN = 2
  BLUE = 3


class EnumTest(test_util.TestCase):

  def testName(self):
    self.assertEquals('RED', Color.RED.name)
    self.assertEquals('GREEN', Color.GREEN.name)
    self.assertEquals('BLUE', Color.BLUE.name)

  def testNumber(self):
    self.assertEquals(1, Color.RED.number)
    self.assertEquals(2, Color.GREEN.number)
    self.assertEquals(3, Color.BLUE.number)

  def testRepr(self):
    self.assertEquals('Color(RED, 1)', repr(Color.RED))
    self.assertEquals('Color(GREEN, 2)', repr(Color.GREEN))
    self.assertEquals('Color(BLUE, 3)', repr(Color.BLUE))

  def testStr(self):
    self.assertEquals('RED', str(Color.RED))
    self.assertEquals('GREEN', str(Color.GREEN))
    self.assertEquals('BLUE', str(Color.BLUE))

  def testInt(self):
    self.assertEquals(1, int(Color.RED))
    self.assertEquals(2, int(Color.GREEN))
    self.assertEquals(3, int(Color.BLUE))

  def testIter(self):
    self.assertEquals((Color.RED, Color.GREEN, Color.BLUE),
                      tuple(Color))

  def testIter(self):
    self.assertEquals((Color.RED, Color.GREEN, Color.BLUE),
                      tuple(Color))

  def testCmp(self):
    class SomeEnum(enum.Enum):

      A = 4
      B = 2
      C = 6
      D = 1
      E = 9

    self.assertEquals([SomeEnum.D,
                       SomeEnum.B,
                       SomeEnum.A,
                       SomeEnum.C,
                       SomeEnum.E,
                       ],
                      sorted(SomeEnum))

  def testConstructor(self):
    self.assertIs(Color.RED, Color('RED'))
    self.assertIs(Color.GREEN, Color('GREEN'))
    self.assertIs(Color.RED, Color(1))
    self.assertIs(Color.GREEN, Color(2))
    self.assertIs(Color.RED, Color(Color.RED))
    self.assertIs(Color.GREEN, Color(Color.GREEN))

  def testConstructorBadParameters(self):
    self.assertRaises(ValueError, Color, None)
    self.assertRaises(ValueError, Color, 'YELLOW')
    self.assertRaises(ValueError, Color, 20)
    self.assertRaises(ValueError, Color, Color)

    class Other(enum.Enum):

      X = 1

    self.assertRaises(ValueError, Color, Other.X)

  def testDuplicateNumber(self):

    def fn():
      class Duppy(enum.Enum):

        A = 1
        B = 1

    self.assertRaises(enum.EnumDefinitionError, fn)


if __name__ == '__main__':
  unittest.main()

