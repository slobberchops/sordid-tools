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

from sordid import util, props


class IllegalStateTransition(Exception):
  pass


class State(util.SourceOrdered, props.HasProps):

  name = props.ReadOnlyProperty()

  machine = props.ReadOnlyProperty()

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


class Transitioner(props.HasProps):

  def __init__(self, machine, transition):
    self.machine = machine
    self.__transition = transition

  machine = props.ReadOnlyProperty()

  @property
  def transition(self):
    return self.__transition

  def __call__(self):
    next_state = self.next_state
    if next_state is None:
      raise IllegalTransitionError(
        'There is no transition %s from state %s for %s' % (
          self.transition.name, current_state, self.__transition))
    self.machine.state = next_state
    return next_state

  @property
  def next_state(self):
    assert self.machine is not None
    return self.transition.get_next_state_from(self.machine.state)


class Transition:

  def __init__(self, state_map):
    super(Transition, self).__init__()
    if isinstance(state_map, dict):
      state_iterator = state_map.items()
    else:
      state_iterator = iter(state_map)

    final_state_map = {}
    seen_froms = set()
    for froms, to in state_map.items():
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


class Machine(props.HasProps):

  def __init__(self):
    try:
      initial_state = self.INIT
    except AttributeError:
      pass
    else:
      self.state = initial_state

    for name, transition in type(self).iter_transitions():
      assert transition is not None
      setattr(self, name, Transitioner(self, transition))

  @classmethod
  def __config_props__(cls, attrs):
    cls.__state_by_name = {}
    cls.__transition_by_name = {}
    for name, value in attrs.items():
      props.config_prop(cls, name, value)

    cls.state_names = sorted(cls.__state_by_name.values(),
                             key=lambda state: state.source_order)

    if cls.__state_by_name:
      first_state_name = cls.state_names[0]
      try:
        cls.INIT = first_state_name
      except AttributeError:
        pass

  @classmethod
  def __config_prop__(cls, name, value):
    if not props.config_prop_name(cls, name, value):
      if isinstance(value, State):
        value.name = name
        value.machine = cls
        cls.__state_by_name[name] = value
      if isinstance(value, Transition):
        cls.__transition_by_name[name] = value

  @classmethod
  def lookup_state(cls, name):
    return cls.__state_by_name.get(name, None)

  @classmethod
  def lookup_transition(cls, name):
    return cls.__transition_by_name.get(name, None)

  @classmethod
  def iter_transitions(cls):
    return cls.__transition_by_name.items()

  INIT = props.ReadOnlyProperty()

  state = props.ValidatedProperty(props.type_validator(State))

  state_names = props.ReadOnlyProperty()
