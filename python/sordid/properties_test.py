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

import mox

from sordid import properties


class ConfigPropNameTest(mox.MoxTestBase):

  def setUp(self):
    super(ConfigPropNameTest, self).setUp()
    class TargetClass(object):
      pass
    self.target_class = TargetClass

  def testNotConfigurable(self):
    for unconfigurable in (1, None, [], {}, 'str'):
      self.assertFalse(
        properties.config_prop_name(self.target_class, 'a', unconfigurable))

  def testConfigurable(self):
    configurable = self.mox.CreateMockAnything()
    configurable.__config__(self.target_class, 'a')

    self.mox.ReplayAll()

    self.assertTrue(
      properties.config_prop_name(self.target_class, 'a', configurable))

  def testClassNotType(self):
    for not_class in (1, None, [], {}, 'str'):
      self.assertRaises(TypeError,
                        properties.config_prop_name,
                        not_class, 'a', 'does not matter')

  def testNameNotString(self):
    for not_string in (1, None, [], {}, object):
      self.assertRaises(TypeError,
                        properties.config_prop_name,
                        self.target_class, not_string, 'does not matter')

  def testNameEmpty(self):
    self.assertRaises(ValueError,
                      properties.config_prop_name,
                      self.target_class, '', 'does not matter')


class ConfigPropTest(mox.MoxTestBase):

  def DoCustomConfigPropTest(self, is_prop):
    class TargetClass(object):

      __config_prop__ = self.mox.CreateMockAnything()

    TargetClass.__config_prop__('a', 'prop1').AndReturn(is_prop)
    self.mox.ReplayAll()

    self.assertEquals(is_prop,
                      properties.config_prop(TargetClass, 'a', 'prop1'))

  def testCustomConfigPropTrue(self):
    self.DoCustomConfigPropTest(True)

  def testCustomConfigPropFalse(self):
    self.DoCustomConfigPropTest(False)

  def testConfigProp(self):
    class TargetClass(object):
      pass

    # Test will pretend to be property.
    self.__config__ = self.mox.CreateMockAnything()
    self.__config__(TargetClass, 'a')

    self.mox.ReplayAll()

    self.assertEquals(True,
                      properties.config_prop(TargetClass, 'a', self))

  def testJustAttributes(self):

    class TargetClass(object):
      name = 'do not overwrite'
      
      def a_method(self):
        pass

      @classmethod
      def a_class_method(cls):
        pass

    for not_property in (10, 'str', [], {}, None, TargetClass, TargetClass(),
                         TargetClass.a_method, TargetClass.a_class_method):
      self.assertFalse(properties.config_prop(TargetClass, 'a', not_property))
      if not_property == TargetClass or isinstance(not_property, TargetClass):
        self.assertEquals('do not overwrite', TargetClass.name)
      else:
        self.assertFalse(hasattr(not_property, 'name'),
                         'Value \'%r\' has a name' % (not_property,))


class ConfigPropsTest(mox.MoxTestBase):

  def testCustomConfigPropsMethod(self):
    class TargetClass(object):
      __config_props__ = self.mox.CreateMockAnything()

    attrs = {'a': 1}

    TargetClass.__config_props__({'a': 1})

    self.mox.ReplayAll()

    properties.config_props(TargetClass, {'a': 1})

  def testCustomConfigPropMethod(self):
    
    class TargetClass(object):
      __config_prop__ = self.mox.CreateMockAnything()

    attrs = {'a': 1, 'b': 2}

    TargetClass.__config_prop__('a', 1).AndReturn(False)
    TargetClass.__config_prop__('b', 2).AndReturn(True)

    self.mox.ReplayAll()

    properties.config_props(TargetClass, {'a': 1, 'b': 2})

  def testCustomConfig(self):
    prop1 = self.mox.CreateMockAnything()
    prop2 = self.mox.CreateMockAnything()
    
    class TargetClass(object):
      pass

    prop1.__config__(TargetClass, 'a')
    prop2.__config__(TargetClass, 'b')

    self.mox.ReplayAll()

    properties.config_props(TargetClass, {'a': prop1, 'b': prop2})

  def testStillConstrains(self):
    self.__config__ = self.mox.CreateMockAnything()
    
    class TargetClass(object):
      pass

    self.mox.ReplayAll()

    self.assertRaises(TypeError,
                      properties.config_props, TargetClass, {1: self})


class PropertiedTypeTest(mox.MoxTestBase):

  def testMetaClass(self):
    self.mox.StubOutWithMock(properties, 'config_props')

    properties.config_props(mox.Func(lambda c: c.__name__ == 'MyClass'),
                            {'__module__': __name__,
                             '__metaclass__': properties.PropertiedType,
                             'a': 'a',
                             'b': 'b',
                             })
                             

    self.mox.ReplayAll()

    class MyClass(object):

      __metaclass__ = properties.PropertiedType

      a = 'a'
      b = 'b'


class PropDesc(object):

  cls = None
  name = None

  def __config__(self, cls, name):
    self.cls = cls
    self.name = name


class PropertiedTest(mox.MoxTestBase):

  def testMetaClass(self):
    self.mox.StubOutWithMock(properties, 'config_props')

    properties.config_props(mox.Func(lambda c: c.__name__ == 'MySubClass'),
                            {'__module__': __name__,
                             'a': 1,
                             'b': 2,
                             })
                             

    self.mox.ReplayAll()

    class MySubClass(properties.Propertied):

      a = 1
      b = 2

  def testSimpleEndToEnd(self):
    prop1 = PropDesc()
    prop2 = PropDesc()

    class MySubClass(properties.Propertied):

      a = 1
      b = 2
      p1 = prop1
      p2 = prop2

    self.assertEquals(MySubClass, prop1.cls)
    self.assertEquals('p1', prop1.name)

    self.assertEquals(MySubClass, prop2.cls)
    self.assertEquals('p2', prop2.name)


class HasPropsTest(mox.MoxTestBase):

  def testHasNoProperties(self):

    class HasNoProps(properties.HasProps):
      pass

    self.assertEquals(set(), set(HasNoProps.prop_names()))
    self.assertEquals(set(), set(HasNoProps.props()))

  def testHasOnlyAttrs(self):

    class HasOnlyAttrs(properties.HasProps):
      a = 1
      b = 2

    self.assertEquals(set(), set(HasOnlyAttrs.prop_names()))
    self.assertEquals(set(), set(HasOnlyAttrs.props()))

  def testHasProps(self):

    class HasProps(properties.HasProps):
      a = PropDesc()
      b = PropDesc()

    self.assertEquals(set(['a', 'b']), set(HasProps.prop_names()))
    self.assertEquals(set([('a', HasProps.a),
                           ('b', HasProps.b)
                          ]),
                      set(HasProps.props()))


if __name__ == '__main__':
  unittest.main()
