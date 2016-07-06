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

class IllegalStateError(Exception):
  """Raised when a class is used in an incorrect state."""


def positional(max_positional_arguments):
  """A decorator to declare that only the first N arguments my be positional.

  This decorator makes it easy to support Python 3 style key-word only
  parameters.  For example, in Python 3 it is possible to write:

    def fn(pos1, *, kwonly1=None, kwonly1=None):
      ...

  All named parameters after * must be a keyword:

    fn(10, 'kw1', 'kw2')  # Raises exception.
    fn(10, kwonly1='kw1')  # Ok.

  Borrowed from ProtoRPC:

  http://code.google.com/p/google-protorpc/source/browse/python/protorpc/util.py#50

  Args:
    max_positional_arguments: Maximum number of positional arguments.  All
      parameters after the this index must be keyword only.

  Returns:
    A decorator that prevents using arguments after max_positional_args from
    being used as positional parameters.

  Raises:
    TypeError if a key-word only argument is provided as a positional parameter.
  """
  def positional_decorator(callable):
    def positional_wrapper(*args, **kwargs):
      if len(args) > max_positional_arguments:
        raise TypeError('Call to %s accepts only %d parameters' %
                        (callable.__name__, max_positional_arguments))
      return callable(*args, **kwargs)
    positional_wrapper.__name__ = callable.__name__
    return positional_wrapper
  return positional_decorator


class SourceOrdered(object):
  """Base class that remembers order its instances are created.

  Example:

    class Person(SourceOrdered):
      ...

    daniel = Person()
    tamy = Person()

    assert daniel.source_order < tamy.source_order
  """

  __next_source_order = 0

  def __init__(self):
    self.__source_order = self.__next_source_order
    SourceOrdered.__next_source_order += 1

  @property
  def source_order(self):
    return self.__source_order

  def __str__(self):
    return str(self.__source_order)

  __repr__ = __str__
