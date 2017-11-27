
from . import proputils


class PropertyTestMixin(object):

  def setUp(self):
    self.C = self.new_class()

  def do_test_set_and_delete(self, c):
    c.p = 'x'
    self.assertEquals('x', c.p)
    c.p = 'y'
    self.assertEquals('y', c.p)

    del c.p
    self.assertRaises(AttributeError, getattr, c, 'p')
    self.assertRaises(AttributeError, delattr, c, 'p')

  def testInitialState_ClassAttributes(self):
    self.assertRaises(AttributeError, getattr, self.C.p, 'name')
    self.assertRaises(AttributeError, getattr, self.C.p, 'class')

  def testInitialState_Get(self):
    c = self.C()
    self.assertRaises(AttributeError, getattr, c, 'p')

  def testInitialState_Set(self):
    c = self.C()
    self.assertRaises(AttributeError, setattr, c, 'p', 1)

  def testInitialState_Delete(self):
    c = self.C()
    self.assertRaises(AttributeError, delattr, c, 'p')

  def testGetSetAndDelete(self):
    proputils.config_props(self.C)
    c = self.C()

    self.assertRaises(AttributeError, getattr, c, 'p')
    self.assertRaises(AttributeError, delattr, c, 'p')

    self.do_test_set_and_delete(c)
