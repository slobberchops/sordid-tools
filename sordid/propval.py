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

from . import proputils


class ValidatedProperty(proputils.Property):
  """Property that provides some type of validation.

  Provide a validation function to validate upon assignment each
  value to property.

    Example:

      class UnsignedInt(Propertied):

        @ValidatedProperty
        def value(value):
          return value >= 0

      i = UnsignedInt()
      i.value = 0
      i.value = 1
      i.value = -1  # Raises ValueError
  """

  def __init__(self, validator=None):
    """Constructor.

    Args:
      validator: Validation function that a value meant for assignment to
        property and returns True if valid, else False.
    """
    self.__validator = validator

  def __set__(self, instance, value):
    """Set value of validated property.

    Args:
      instance: Object that will receive property value.
      value: New value for property.

    Raises:
      ValueError: If property is not correct value.
    """
    if not self.__validator(value):
      raise ValueError('Value \'%r\' is not valid '
                       'for property \'%s\' on \'%s\'' % (
                         value, self.name, self.cls.__name__))
    super(ValidatedProperty, self).__set__(instance, value)


class Validator(object):
  """Base class validator class.

  Though not required to make a property validator, this class
  helps make writing them easier by providing some basic operator support.

  It is possible to use binary logical operators to construct validators
  from basic ones.

  Example:

    class Person(Propertied):

      # ID is required to be a non-empty string.
      id = ValidatedProperty(not EMPTY & type_validator(str))

      # Name is required to be a non-empty string or None.
      name = ValidatedProperty(NONE | (not EMPTY & type_validator(str)))

      # The operators will also work normally for any function.  For example
      # 'all' is the builtin python function 'all' which has the signature
      # of a validator.
      nicknames = ValidatedProperty(type_validator(tuple) & all)
  """

  def __init__(self, validator_func):
    """Constructor.

    Args:
      validator_func: Function used for validating a new value.
    """
    self.__validator_func = validator_func

  def __call__(self, value):
    """Allows this validator object to be used as a validator function."""
    return self.__validator_func(value)

  def __and__(self, other):
    """Creates a validator requires both validators to be true."""
    @Validator
    def and_validator(value):
      return self(value) and other(value)
    return and_validator

  def __or__(self, other):
    """Creates a validator requires either validator to be true."""
    @Validator
    def or_validator(value):
      return self(value) or other(value)
    return or_validator

  def __invert__(self):
    """Creates inverse of a validator."""
    @Validator
    def not_validator(value):
      return not self(value)
    return not_validator


def validator_def(definition):
  """Makes validator factory functions always return Validators.

  Helper for wrapping functions that returns configured validators so that
  they always return Validator objects.

  Example:

    @validator_decorator
    def regex_validator(regex):
      compiled_regex = re.compile(regex)
      def regex_validator_func(value):
        return bool(compiled_regex.match(value))
      return regex_validator

    # Operators will work.
    email_validator = regex_validator('.+@.+') | NONE

  Args:
    definition: A validator factory function that takes any number of
      parameters and returns a validator function.

  Returns:
    A validator factory function that takes the same parameters as 'definition'
    and returns a Validator object that wraps 'definitions's returned validator.
  """
  def validator_decorator(*args, **kwargs):
    return Validator(definition(*args, **kwargs))
  validator_decorator.__name__ = definition.__name__
  return validator_decorator


@validator_def
def type_validator(property_type):
  """Create validator that requires specific type.

  Args:
    property_type: The type of the validator.

  Returns:
    Validator that only accepts values of a specific type.
  """
  def type_validator_impl(value):
    if not isinstance(value, property_type):
      raise TypeError('Property must be type %s' % property_type.__name__)
    return True
  return type_validator_impl


@Validator
def NONE(value):
  """Constant validator that requires None value."""
  return value is None


@Validator
def EMPTY(value):
  """Constant validator that requires empty values (allows None)."""
  return not bool(value)


class StrictProperty(ValidatedProperty):
  """Property that resticts values to a particular type.

  Attempting to set a value on a strict property that is not of the
  provided type (other than None) will raise a TypeError.

  Example:

    class Point(HasProps):

      x = StrictProperty(float)
      y = StrictProperty(float)

    point = Point()
    point.x = 10
    point.y = 20

    point.x = '30'  # Raises TypeError
  """

  def __init__(self, property_type):
    """Constructor.

    Args:
      property_type: Type of strict property.  All values assigned to
        property must be of this type.
    """
    validator = type_validator(property_type)
    self.__property_type = property_type
    super(StrictProperty, self).__init__(validator)

  @property
  def property_type(self):
    """Type of property."""
    return self.__property_type


class CMPType(type):

    def __lt__(cls, constant):
        return cls(operator.lt, constant)

    def __le__(cls, constant):
        return cls(operator.le, constant)

    def __gt__(cls, constant):
        return cls(operator.gt, constant)

    def __ge__(cls, constant):
        return cls(operator.ge, constant)


class CMP(Validator, metaclass=CMPType):
    """Comparison validator.

    Validation based on a binary operator.  Meta-class has operator methods overloaded so may be combined using normal
    comparison operators.  For example:

        class Point(HasProps):
            '''A point for a grid 100 units by 100 units.'''

            x = CMP >= 0 & CMP <= 100
            y = CMP >= 0 & CMP <= 100
    """

    def __init__(self, binop, constant):
        """Constructor.

        Args:
            binop: A function that takes two parameters and returns boolean value.
        """
        def validator(value):
            return binop(value, constant)
        self.__binop = binop
        super(CMP, self).__init__(validator)

    @property
    def binop(self):
        """Binop associated with this validator."""
        return self.__binop


@validator_def
def is_in(constant):
    """Create validator to check whether value is in a constant set of values."""
    return lambda value: value in constant

def validated_property_def(validator):
    """Helper function for defining reusable validated classes."""
    class _ValidatedProperty(ValidatedProperty):

        def __init__(self):
            super(_ValidatedProperty, self).__init__(validator)
    return _ValidatedProperty
