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

from sordid import util


class TestPositional(unittest.TestCase):

  def testBasicPositional(self):
    @util.positional(1)
    def fn(first, second):
      self.first = first
      self.second = second

    fn(1, second=2)
    self.assertEquals(1, self.first)
    self.assertEquals(2, self.second)

    fn(first=3, second=4)
    self.assertEquals(3, self.first)
    self.assertEquals(4, self.second)

  def testKeywordAsPositional(self):
    self.first = 0
    @util.positional(0)
    def fn(first):
      self.first = first
  
    try:
      fn(1)
    except TypeError, err:
      self.assertEquals('Call to fn accepts only 0 parameters', str(err))
    else:
      self.fail('Expected type error')

    self.assertEquals(0, self.first)


if __name__ == '__main__':
  unittest.main()
