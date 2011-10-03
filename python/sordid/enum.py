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

from sordid import properties

class EnumDefinitionError(Exception):
  """Raised when enum is incorrectly defined."""


class EnumType(properties.PropertiedType):
  """Enum type meta-class.

  Does automatic initialization of Enum classes.  See Enum for more details.
  """

  __self_ref = None
  __by_name = {}
  __by_number = {}

  def __init__(cls, name, bases, dct):
    cls.__by_name = dict(cls.__by_name)
    cls.__by_number = dict(cls.__by_number)
    for attribute, value in dct.iteritems():
      # Enums may replace attributes, but no attribute may replace
      # an enum.
      if attribute in cls.__by_name:
        raise EnumDefinitionError('Enum %s already has enum value %s' %
                                  (name, attribute))
        
      if isinstance(value, (int, long)):
        if value in cls.__by_number:
          raise EnumDefinitionError('Enum %s already has enum value '
                                    'with number %d' % (name, value))
        enum_value = cls(attribute, value)
        cls.__by_name[attribute] = enum_value
        cls.__by_number[value] = enum_value
        setattr(cls, attribute, enum_value)

    cls.__self_ref = cls
    properties.PropertiedType.__init__(cls, name, bases, dct)

  @staticmethod
  def is_enum_init(enum_class):
    """Determine if provided enum class has been initialized.

    This method is useful for initialization code of a derived Enum class
    so that it can be determined if class definition has been completed or
    not.

    This method most likely has very limited value to users.

    Args:
      enum_class: Enum class.

    Returns:
      True if enum class is initialized, else False.
    """
    return enum_class.__self_ref is enum_class

  @staticmethod
  def lookup_by_name(cls, name):
    """Look up an enum value by name.

    Args:
      name: Name of enum value.

    Returns:
      If name is defined on an enum class, returns associated value, else None.
    """
    return cls.__by_name.get(name, None)

  @staticmethod
  def lookup_by_number(cls, number):
    """Look up an enum value by number.

    Args:
      number: Number of enum value.

    Returns:
      If enum value with number is defined on enum class, returns associated
      value, else None.
    """
    return cls.__by_number.get(number, None)

  @staticmethod
  def lookup(cls, key):
    """Look up an enum value by name or number.

    Args:
      key: Number or name of enum value.  Can also be enum value itself.

    Returns:
      If value can be looked up or is an instance of class, returns associated
      value, else None.
    """
    if isinstance(key, unicode):
      key = key.encode('utf-8')

    if isinstance(key, str):
      return EnumType.lookup_by_name(cls, key)
    elif isinstance(key, (int, long)):
      return EnumType.lookup_by_number(cls, key)
    elif isinstance(key, cls):
      return key
    else:
      return None

  def __iter__(cls):
    """Iterate over an Enum type.

    Returns:
      Iterator over all enum values of a class in their numeric order.
    """
    return cls.__by_number.itervalues()

  def __contains__(cls, value):
    """Determine whether or not a value is in Enum class.

    Args:
      value: String, integer or enum to determine if in Enum type.

    Returns:
      True if value is in Enum else, False.
    """
    return EnumType.lookup(cls, value) is not None


class Enum(object):
  """Enum type base class.

  Used for defining descrete enumated values that have the following properties:
    - Unique name per class.
    - Unique numeric value per class.
    - Stable sorting (by numeric value) for all items in class.
    - Immutability.

  Useful for defining classes of items for which identity is their main feature.
  For example, days of the week:

      class Days(Enum):

        SUNDAY = 1
        MONDAY = 2
        TUESDAY = 3
        WEDNESDAY = 4
        THURSDAY = 5
        FRIDAY = 6
        SATURDAY = 7

  Each item in an enumerated type that has a numeric value is converted to
  an instance of its containing class.  For example, the following:

      assert isinstance(Days.TUESDAY, Days)

  Each item knows its own string and numeric value.

      assert 'Monday' == Days.MONDAY.name
      assert 2 == Days.MONDAY.name

  For convenience, an enumerated value is convertable to an int or str:

      assert 'Monday' == str(Days.MONDAY)
      assert 2 == int(Days.MONDAY)

  It is possible to enumerate over all values of the enum type by iterating
  over the class.  The values are enumerated in numeric order.

      iterator = iter(Days)
      assert Days.SUNDAY is iterator.next()
      assert Days.MONDAY is iterator.next()

  Enum values are by default sorted in numeric order.

  Values of enum types can be easily converted from string and integer values
  using the constructor.  The constructor will always return the singleton
  instance of an enum value.  It is not possible to create any more enum
  values on a class once it has finished initializing.

      assert Days.Monday is Days('Monday')
      assert Days.Monday is Days(2)
      assert Days.Monday is Days(Days.MONDAY)
  """

  __metaclass__ = EnumType

  def __new__(cls, name, number=None):
    if EnumType.is_enum_init(cls):
      value = EnumType.lookup(cls, name)
      if value is None:
        raise ValueError('No such enum for %s: "%r"' % (
          cls.__name__, name))
      return value
    else:
      return super(Enum, cls).__new__(cls)

  def __init__(self, name, number=None):
    if (EnumType.is_enum_init(type(self))):
        return
    if EnumType.is_enum_init(self):
      raise util.IllegalStateError('Enum class %s is already initialized' %
                                   type(self).__name__)
    self.__name = name
    self.__number = number

  @property
  def name(self):
    return self.__name

  @property
  def number(self):
    return self.__number

  def __repr__(self):
    return '%s(%s, %d)' % (type(self).__name__, self.__name, self.__number)

  def __str__(self):
    return self.__name

  def __int__(self):
    return self.__number

  def __cmp__(self, other):
    return cmp(int(self), int(other))
