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

from sordid import util


class Property(object):
  """A property base class.

  This class implements a Python descriptor object:

    http://docs.python.org/reference/datamodel.html#descriptors

  When used in conjection with the PropertiedType meta-class or Propertied
  class it is possible to build reusable declarative properties that more
  clearly define how a property is intended to be used.

  An instance of a Property is meant to be associated with a single name
  on a single class.

  Each property has a 'configure' method to properly sets up the property
  for use with an associated class.  The default behavior of 'configure' is
  to indicate to the property what its name will be and to tell it which class
  it is associated with.  The value of a property for an instance of the
  assigned class is stored on a private variable of the target class.
  """

  __name = None

  def configure(self, cls, name):
    if self.__name:
      raise IllegalStateError('Property is already configured')
    self.__name = name
    self.__attribute_name = '_%s__%s' % (cls.__name__, name)

  @property
  def name(self):
    return self.__name

  def __get_property__(self, owner):
    return self

  def __get_value__(self, instance, owner):
    return getattr(instance, self.__attribute_name)

  def __get__(self, instance, owner):
    if instance is None:
      return self.__get_property__(owner)
    else:
      if self.__name is None:
        raise util.IllegalStateError('Property name has not been assigned to '
                                     'attribute yet')
      return self.__get_value__(instance, owner)

  def __set__(self, instance, value):
    if self.__name is None:
      raise util.IllegalStateError('Property name has not been assigned to '
                                   'attribute yet')
    setattr(instance, self.__attribute_name, value)


class PropertiedType(type):
  """Meta-class that will automatically configure properties on a class.

  Use this meta-class to make a class that will automatically configure classes
  which are assigned to it.

  For example, one can use StrictProperty to ensure that only certain types can
  be assigned to an attribute:

    class Person(object):

      __metaclass__ = PropertiedType

      name = StrictType(unicode)
      age = StrictType(int)

    daniel = Person()
    daniel.name = u'Daniel'
    daniel.age = 28

    # do incorrect assignment
    daniel.name = 1020  # Raises TypeError

  When a Property instance is assigned to a class attribute of a PropertiedType
  the class it is being assigned to and the name of the property are
  automatically sent to the Property's 'configure' method.  The above definition
  is the same as doing:

    class Person(object):

      name = StrictType(unicode)
      age = StrictType(int)

    Person.name.configure(Person, 'name')
    Person.age.configure(Person, 'age')
  """

  def __init__(cls, name, bases, dct):
    for attribute, value in dct.iteritems():
      if isinstance(value, Property):
        value.configure(cls, attribute)


class Propertied(object):
  """Convenient base class for defining classes with properties.

  For example:

    class Person(Propertied):

      name = StrictType(unicode)
      age = StrictType(int)
  """

  __metaclass__ = PropertiedType


class StrictProperty(Property):
  """Property that resticts values to a particular type.

  Attempting to set a value on a strict property that is not of the
  provided type (other than None) will raise a TypeError.
  """

  def __init__(self, property_type):
    self.__property_type = property_type

  @property
  def property_type(self):
    return self.__property_type

  def __set__(self, instance, value):
    if not(value is None or isinstance(value, self.__property_type)):
      raise TypeError('Property \'%s\' must be type %s' % (
        self.name, self.__property_type.__name__))
    super(StrictProperty, self).__set__(instance, value)


class ReadOnlyProperty(Property):
  """Property that may only be set once with non-None value."""

  def __set__(self, instance, value):
    current_value = getattr(instance, self.name, None)
    if current_value is not None:
      raise util.IllegalStateError('Property \'%s\' is already configured' %
                                   self.name)
    super(ReadOnlyProperty, self).__set__(instance, value)

