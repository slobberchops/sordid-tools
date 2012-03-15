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


def config_props(cls, attrs):
  """Configure all properties found on a class instance.

  Attempts to configure all properties of a class.  If class has
  __config_props__ class method, will delegate configuration to it.
  Otherwise, it iterates over all attributes and calls config_prop
  on it.

  Args:
    cls: Class with properties in need of configuration.
    attrs: Dictionary of attributes.
  """
  try:
    cls_config_props = cls.__config_props__
  except AttributeError:
    for name, value in attrs.iteritems():
      config_prop(cls, name, value)
  else:
    cls_config_props(attrs)


def config_prop(cls, name, value):
  """Configure property on class.

  Attempts to configure single property on a class.  If class has
  __config_prop__ class method will use that it configure property.
  Otherwise it will call config_prop_name on property.

  Args:
    cls: Class with property in need of configuration.
    name: Name of attribute.
    value: Value of attribute.

  Returns:
    True if attribute was determined to be a property and was configured,
    else False.
  """
  try:
    cls_config_prop = cls.__config_prop__
  except AttributeError:
    return config_prop_name(cls, name, value)
  else:
    return cls_config_prop(name, value)


def config_prop_name(cls, name, value):
  """Configure name on property.

  Attempts to configure the name of a property.  If attribute value has
  __config__ method will call it with attribute name.

  Args:
    cls: Class property will belong to.
    name: Name of attribute.
    value: Value of attribute.

  Returns:
    True if attribute was determined to be a property and was configured,
    else False.
  """
  if not isinstance(cls, type):
    raise TypeError('Class must be a type')
  if not isinstance(name, str):
    raise TypeError('Name must be a string')
  if not name:
    raise ValueError('Name must be non-empty')

  try:
    config = value.__config__
  except AttributeError:
    return False
  else:
    config(cls, name)
    return True


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
  automatically sent to the Property's '__config__' method.  The above definition
  is the same as doing:

    class Person(object):

      name = StrictType(unicode)
      age = StrictType(int)

    Person.name.__config__('name')
    Person.age.__config__('age')
  """

  def __init__(cls, name, bases, dct):
    config_props(cls, dct)


class Propertied(object):
  """Convenient base class for defining classes with properties.

  For example:

    class Person(Propertied):

      name = StrictType(unicode)
      age = StrictType(int)
  """

  __metaclass__ = PropertiedType


class HasProps(Propertied):
  """Convenient base class for properties classes that know their properties.

  Classes that inherit from this class will remember what properties it has and
  provide methods for enumerating those properties.

  Properties are inherited from base classes but can be overridden.
  """

  @classmethod
  def __config_props__(cls, attrs):
    """Configures and rememberes class properties."""
    try:
      cls.__props = dict(cls.__props.iteritems())
    except AttributeError:
      cls.__props = {}
    for name, value in attrs.iteritems():
      config_prop(cls, name, value)
    cls.__prop_names = frozenset(cls.__props.iterkeys())
    cls.__prop_set = frozenset(cls.__props.iteritems())

  @classmethod
  def __config_prop__(cls, name, value):
    """Configures and potentially remembers a single property."""
    if config_prop_name(cls, name, value):
      cls.__props[name] = value

  @classmethod
  def prop_names(cls):
    """Iterable of all property names."""
    return cls.__prop_names

  @classmethod
  def props(cls):
    """Iterable of all property descriptors."""
    return cls.__prop_set
