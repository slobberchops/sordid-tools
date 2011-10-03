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

from sordid import properties
from sordid import util


p1 = properties.Property()
class MyClass(object):
  property1 = p1


class  PropertyTest(unittest.TestCase):

  def testStaticAccess(self):
    self.assertEquals(id(p1), id(MyClass.property1))

  def testSetGet(self):
    instance = MyClass()
    try:
      instance.property1
    except util.IllegalStateError, err:
      self.assertEquals('Property name has not been assigned to attribute yet',
                        str(err))
    else:
      self.fail('Should have been an illegal state')

    try:
      instance.property1 = 10
    except util.IllegalStateError, err:
      self.assertEquals('Property name has not been assigned to attribute yet',
                        str(err))
    else:
      self.fail('Should have been an illegal state')

  def testSetAndGet(self):
    class WorkingClass(object):

      property1 = properties.Property()

    WorkingClass.property1.configure(WorkingClass, 'property1')
    self.assertEquals('property1', WorkingClass.property1.name)

    instance = WorkingClass()

    try:
      instance.property1
    except AttributeError:
      pass
    else:
      self.fail('Should have been an attribute error')

    test_string = 'a value'
    instance.property1 = test_string
    self.assertEquals(id(test_string), id(instance.property1))


class MyPropertied(object):

  __metaclass__ = properties.PropertiedType

  auto_configured = properties.Property()


class PropertiedTypeTest(unittest.TestCase):

  def testAutoConfigured(self):
    self.assertEquals('auto_configured', MyPropertied.auto_configured.name)
    propertied = MyPropertied()
    test_string = 'a_string'
    propertied.auto_configured = test_string
    self.assertEquals(id(test_string), id(propertied.auto_configured))


class HasStrict(properties.Propertied):

  string = properties.StrictProperty(str)
  integer = properties.StrictProperty(int)
  multi = properties.StrictProperty((int, str))


class StrictPropertyTest(unittest.TestCase):

  def testAssignment(self):
    strict = HasStrict()
    test_string = 'a string'
    strict.string = test_string
    self.assertEquals(id(test_string), id(strict.string))

    test_integer = 340
    strict.integer = test_integer
    self.assertEquals(id(test_integer), id(strict.integer))

  def testIllegalAssignment(self):
    strict = HasStrict()

    try:
      strict.string = 304
    except TypeError, err:
      self.assertEquals('Property \'string\' must be type str', str(err))
    else:
      self.fail('Should have been a TypeError')

    try:
      strict.integer = 'a string'
    except TypeError, err:
      self.assertEquals('Property \'integer\' must be type int', str(err))
    else:
      self.fail('Should have been a TypeError')


class ReadOnlyPropertyTest(unittest.TestCase):

  def testReadOnly(self):
    class HasReadOnly(properties.Propertied):
      read_only = properties.ReadOnlyProperty()

    instance = HasReadOnly()
    test_string = 'a string'
    instance.read_only = test_string
    self.assertEquals(id(test_string), id(instance.read_only))

    try:
      instance.read_only = 'another value'
    except util.IllegalStateError, err:
      self.assertEquals('Property \'read_only\' is already configured',
                        str(err))
    else:
      self.fail('Should have been IllegalStateException')


if __name__ == '__main__':
  unittest.main()
