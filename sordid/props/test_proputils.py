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

import unittest

from mox3 import mox

from sordid.props import proputils
from sordid.props import prop_testutils


class ConfigPropNameTest(mox.MoxTestBase):

  def setUp(self):
    super(ConfigPropNameTest, self).setUp()
    class TargetClass(object):
      pass
    self.target_class = TargetClass

  def testNotConfigurable(self):
    for unconfigurable in (1, None, [], {}, 'str'):
      self.assertFalse(
        proputils.config_prop_name(self.target_class, 'a', unconfigurable))

  def testConfigurable(self):
    configurable = self.mox.CreateMockAnything()
    configurable.__config__(self.target_class, 'a')

    self.mox.ReplayAll()

    self.assertTrue(
      proputils.config_prop_name(self.target_class, 'a', configurable))

  def testClassNotType(self):
    for not_class in (1, None, [], {}, 'str'):
      self.assertRaises(TypeError,
                        proputils.config_prop_name,
                        not_class, 'a', 'does not matter')

  def testNameNotString(self):
    for not_string in (1, None, [], {}, object):
      self.assertRaises(TypeError,
                        proputils.config_prop_name,
                        self.target_class, not_string, 'does not matter')

  def testNameEmpty(self):
    self.assertRaises(ValueError,
                      proputils.config_prop_name,
                      self.target_class, '', 'does not matter')


class ConfigPropTest(mox.MoxTestBase):

  def DoCustomConfigPropTest(self, is_prop):
    class TargetClass(object):

      __config_prop__ = self.mox.CreateMockAnything()

    TargetClass.__config_prop__('a', 'prop1').AndReturn(is_prop)
    self.mox.ReplayAll()

    self.assertEquals(is_prop,
                      proputils.config_prop(TargetClass, 'a', 'prop1'))

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
                      proputils.config_prop(TargetClass, 'a', self))

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
      self.assertFalse(proputils.config_prop(TargetClass, 'a', not_property))
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

    TargetClass.__config_props__(attrs)

    self.mox.ReplayAll()

    proputils.config_props(TargetClass, attrs)

  def testCustomConfigPropMethod(self):
    
    class TargetClass(object):
      __config_prop__ = self.mox.CreateMockAnything()

    mox.UnorderedGroup
    TargetClass.__config_prop__('a', 1).InAnyOrder().AndReturn(False)
    TargetClass.__config_prop__('b', 2).InAnyOrder().AndReturn(True)

    self.mox.ReplayAll()

    proputils.config_props(TargetClass, {'a': 1, 'b': 2})

  def testCustomConfig(self):
    prop1 = self.mox.CreateMockAnything()
    prop2 = self.mox.CreateMockAnything()
    
    class TargetClass(object):
      pass

    prop1.__config__(TargetClass, 'a')
    prop2.__config__(TargetClass, 'b')

    self.mox.ReplayAll()

    proputils.config_props(TargetClass, {'a': prop1, 'b': prop2})

  def testStillConstrains(self):
    class TargetClass(object):
      pass

    self.mox.ReplayAll()

    self.assertRaises(TypeError,
                      proputils.config_props, TargetClass, {1: self})

  def testNotAttrs(self):

    class TargetClass(object):

      __config_props__ = self.mox.CreateMockAnything()
      a = 1
      b = 'str'

    attrs = dict((n, getattr(TargetClass, n)) for n in dir(TargetClass))
    TargetClass.__config_props__(attrs)

    self.mox.ReplayAll()

    proputils.config_props(TargetClass)


class PropertiedTypeTest(mox.MoxTestBase):

  def testMetaClass(self):
    self.mox.StubOutWithMock(proputils, 'config_props')

    proputils.config_props(mox.Func(lambda c: c.__name__ == 'MyClass'),
                           {'__module__': __name__,
                             '__qualname__': 'PropertiedTypeTest.testMetaClass.<locals>.MyClass',
                             'a': 'a',
                             'b': 'b',
                             })

    self.mox.ReplayAll()

    class MyClass(object, metaclass=proputils.PropertiedType):

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
    self.mox.StubOutWithMock(proputils, 'config_props')

    proputils.config_props(mox.Func(lambda c: c.__name__ == 'MySubClass'),
                           {'__module__': __name__,
                            '__qualname__': 'PropertiedTest.testMetaClass.<locals>.MySubClass',
                            'a': 1,
                            'b': 2,
                           })


    self.mox.ReplayAll()

    class MySubClass(proputils.Propertied):

      a = 1
      b = 2

  def testSimpleEndToEnd(self):
    prop1 = PropDesc()
    prop2 = PropDesc()

    class MySubClass(proputils.Propertied):

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

    class HasNoProps(proputils.HasProps):
      pass

    self.assertEquals(set(), set(HasNoProps.prop_names()))
    self.assertEquals(set(), set(HasNoProps.props()))

  def testHasOnlyAttrs(self):

    class HasOnlyAttrs(proputils.HasProps):
      a = 1
      b = 2

    self.assertEquals(set(), set(HasOnlyAttrs.prop_names()))
    self.assertEquals(set(), set(HasOnlyAttrs.props()))

  def testHasProps(self):

    class HasProps(proputils.HasProps):
      a = PropDesc()
      b = PropDesc()

    self.assertEquals(set(['a', 'b']), set(HasProps.prop_names()))
    self.assertEquals(set([('a', HasProps.a),
                           ('b', HasProps.b)
                          ]),
                      set(HasProps.props()))

    hp = HasProps()
    hp.a = 1
    hp.b = 2
    self.assertEquals(1, hp.a)
    self.assertEquals(2, hp.b)

  def testHasPropsSubclass(self):

    class MyHasProps(proputils.HasProps):
      a = PropDesc()
      b = PropDesc()

    class MyHasPropsSub(MyHasProps):
      b = PropDesc()
      c = PropDesc()

    self.assertEquals(set(['a', 'b', 'c']), set(MyHasPropsSub.prop_names()))
    self.assertEquals(set([('a', MyHasPropsSub.a),
                           ('b', MyHasPropsSub.b),
                           ('c', MyHasPropsSub.c),
                          ]),
                      set(MyHasPropsSub.props()))
    self.assertNotEquals(MyHasProps.b, MyHasPropsSub.b)

    hp = MyHasPropsSub()
    hp.a = 1
    hp.b = 2
    hp.c = 3
    self.assertEquals(1, hp.a)
    self.assertEquals(2, hp.b)
    self.assertEquals(3, hp.c)

  def testNoStrangeInternalState(self):

    class BadDict(object):
      def iteritems(self):
        raise AttributeError('unexpected')

    class MyHasProps(proputils.HasProps):
      pass
    MyHasProps._HasProps__props = BadDict()

    def new_subclass():
      class MyHasPropsSubclass(MyHasProps):
        pass
    self.assertRaises(AttributeError, new_subclass)


class PropertyTest(prop_testutils.PropertyTestMixin, unittest.TestCase):

  def new_class(self):
    class C(object):
      p = proputils.Property()
    return C

  def testOverridableGetProperty(self):

    class CalcProp(proputils.Property):

      def __init__(self):
        self.count = 0

      def __get_property__(self, instance):
        self.count += 1
        return 'I am calculated: %d' % self.count

    class HasCalc(proputils.Propertied):
      calc = CalcProp()

    instance = HasCalc()
    self.assertEquals('I am calculated: 1', instance.calc)
    self.assertEquals('I am calculated: 2', instance.calc)
    instance.calc = 'new val'
    self.assertEquals('I am calculated: 3', instance.calc)

  def testUnconfiguredClsReference(self):
    prop = proputils.Property()
    with self.assertRaisesRegex(AttributeError, 'Property not configured'):
      prop.cls

  def testConfigTwice(self):
    class Owner(proputils.Propertied):
      prop1 = proputils.Property()

    with self.assertRaisesRegex(TypeError,
                                'Property \'prop1\' is already configured '
                                'on class \'Owner\''):
      proputils.config_prop(Owner, 'prop2', Owner.prop1)
    self.assertEqual('prop1', Owner.prop1.name)


class UndeletablePropertyTest(prop_testutils.PropertyTestMixin, unittest.TestCase):

  def new_class(self):
    class C(object):
      p = proputils.UndeletableProperty()
    return C

  def do_test_set_and_delete(self, c):
    c.p = 'x'
    self.assertEquals('x', c.p)
    c.p = 'y'
    self.assertEquals('y', c.p)

    self.assertRaises(AttributeError, delattr, c, 'p')
    self.assertEquals('y', c.p)


class UsettablePropertyTest(prop_testutils.PropertyTestMixin, unittest.TestCase):

  def new_class(self):
    class C(object):
      p = proputils.UnsettableProperty()
    return C

  def do_test_set_and_delete(self, c):
    with self.assertRaisesRegex(AttributeError,
                                '\'p\' object attribute \'C\' is read-only'):
      c.p = 'x'


class ReadOnlyPropertyTest(prop_testutils.PropertyTestMixin, unittest.TestCase):

  def new_class(self):
    class C(object):
      p = proputils.ReadOnlyProperty()
    return C

  def do_test_set_and_delete(self, c):
    c.p = 'x'
    self.assertEquals('x', c.p)
    self.assertRaises(AttributeError, setattr, c, 'p', 'y')
    self.assertEquals('x', c.p)

    self.assertRaises(AttributeError, delattr, c, 'p')
    self.assertEquals('x', c.p)


def computed_property_callable(self):
  return 'computed-property:' + self.on_self


class ComputedPropertyTest(prop_testutils.PropertyTestMixin, unittest.TestCase):

  def new_class(self):
    class C(object):

      def __init__(self):
        self.on_self = 'abc'

      p = proputils.ComputedProperty(computed_property_callable)

    return C

  def testGetSetAndDelete(self):
    proputils.config_props(self.C)
    c = self.C()

    self.assertEqual('computed-property:abc', c.p)
    with self.assertRaisesRegex(AttributeError, '\'p\' object attribute \'C\' is read-only'):
      del c.p

    with self.assertRaisesRegex(AttributeError, '\'p\' object attribute \'C\' is read-only'):
      c.p = 'another-value'

    self.assertEqual('computed-property:abc', c.p)

  def test_callable(self):
    self.assertIs(computed_property_callable, self.C.p.callable)

  def test_non_callable(self):
    with self.assertRaisesRegex(TypeError, 'callable_object must be callable'):
      proputils.ComputedProperty('non-callable')

if __name__ == '__main__':
  unittest.main()
