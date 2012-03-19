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

import datetime

from sordid import proputils
from sordid import util

class IllegalStateTransition(Exception):
  pass


class State(util.SourceOrdered):

  @property
  def name(self):
    return self.__name

  @property
  def machine(self):
    return self.__machine

  def __str__(self):
    try:
      return self.__string_value
    except AttributeError:
      name = getattr(self, 'name', None)
      if name is not None:
        name_value = name
      else:
        name_value = 'UNKNOWN'

      machine = getattr(self, 'machine', None)
      if machine is not None:
        machine_name = machine.__name__
      else:
        machine_name = 'UNASSIGNED'

      current_name = '%s::%s' % (machine_name, name_value)
      if name is not None and machine is not None:
        self.__string_value = current_name
      return current_name
    return self.__string_value


class Transitioner(object):

  def __init__(self, machine, transition):
    self.__machine = machine
    self.__transition = transition

  @property
  def machine(self):
    return self.__machine

  @property
  def transition(self):
    return self.__transition

  def __call__(self):
    next_state = self.next_state
    if next_state is None:
      raise IllegalTransitionError(
        'There is no transition %s from state %s for %s' % (
          self.transition.name, current_state, self.__transition))
    self.machine.set_state(next_state)
    return next_state

  @property
  def next_state(self):
    assert self.machine is not None
    return self.transition.get_next_state_from(self.machine.state)


class Transition(object):

  def __init__(self, state_map):
    super(Transition, self).__init__()
    if isinstance(state_map, dict):
      state_iterator = state_map.iteritems()
    else:
      state_iterator = iter(state_map)

    final_state_map = {}
    seen_froms = set()
    for froms, to in state_map.iteritems():
      if isinstance(froms, State):
        froms = [froms]
      for next_from in froms:
        if next_from in seen_froms:
          raise AssertionError('State %s is already defined for transition' %
                               next_from)
        final_state_map[next_from] = to
      self.__state_map = final_state_map

  def get_next_state_from(self, state):
    return self.__state_map.get(state, None)


class Machine(object):

  class __metaclass__(proputils.PropertiedType):

    def __init__(cls, name, bases, dct):
      type.__init__(cls, name, bases, dct)
      state_by_name = {}
      transition_by_name = {}
      for attribute, value in dct.iteritems():
        if isinstance(value, State) and attribute != 'INIT':
          value._State__name = attribute
          value._State__machine = cls
          state_by_name[attribute] = value
        if isinstance(value, Transition):
          transition_by_name[attribute] = value

      cls.__state_by_name = state_by_name
      cls.__transition_by_name = transition_by_name

      if len(state_by_name) > 0:
        initial_state = getattr(cls, '_Machine__INIT', None)
        if initial_state is None:
          states = sorted(state_by_name.itervalues(),
                          key=lambda state: state.source_order)
          cls._Machine__INIT = states[0]

    def lookup_state(cls, name):
      return cls.__state_by_name.get(name, None)

    def lookup_transition(cls, name):
      return cls.__transition_by_name.get(name, None)

    def iter_transitions(cls):
      return cls.__transition_by_name.iteritems()

  def __init__(self):
    try:
      initial_state = self.__INIT
    except AttributeError:
      initial_state = None
    self.set_state(initial_state)

    for name, transition in type(self).iter_transitions():
      assert transition is not None
      setattr(self, name, Transitioner(self, transition))

  @property
  def INIT(self):
    return self.__INIT

  def set_state(self, state):
    self.__state = state

  @property
  def state(self):
    return self.__state
   
