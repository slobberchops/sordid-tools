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

from sordid import machine


class MachineTest(unittest.TestCase):

  def testEmptyMachine(self):
    class EmptyMachine(machine.Machine):
      pass

    mach = machine.Machine()
    self.assertEquals(None, mach.state)

  def testInitialStateDocumentOrder(self):
    class Alphabetical(machine.Machine):
      a = machine.State()
      b = machine.State()
    mach = Alphabetical()
    self.assertEquals(Alphabetical.a, mach.state)

    class Reversed(machine.Machine):
      b = machine.State()
      a = machine.State()
    mach = Reversed()
    self.assertEquals(Reversed.b, mach.state)

  def testGetNextStateFrom(self):
    class HasTransition(machine.Machine):
      a = machine.State()
      b = machine.State()
      c = machine.State()

      A = machine.Transition({
        a: b,
        c: a
      })

    mach = HasTransition()
    self.assertEquals(HasTransition.b,
                      mach.A.next_state)
    mach.set_state(mach.b)
    self.assertEquals(None,
                      mach.A.next_state)
    mach.set_state(mach.c)
    self.assertEquals(HasTransition.a,
                      mach.A.next_state)

  def testDoTransition(self):
    class Mach(machine.Machine):
      a = machine.State()
      b = machine.State()
      c = machine.State()

      A = machine.Transition({
        a: b,
      })

    mach = Mach()
    self.assertEquals(Mach.a, mach.state)
    self.assertEquals(Mach.b, mach.A())
    self.assertEquals(Mach.b, mach.state)
    

if __name__ == '__main__':
  unittest.main()
