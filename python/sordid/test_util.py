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

import CGIHTTPServer
import httplib
import socket
import sys
import threading
import time
import unittest
from wsgiref import simple_server
from wsgiref import validate

def pick_unused_port():
  """Find an unused port to use in tests.

  Copied from ProtoRPC:

    http://code.google.com/p/google-protorpc/source/browse/python/protorpc/test_util.py#541

  Derived from Damon Kohlers example:

    http://code.activestate.com/recipes/531822-pick-unused-port
  """
  temp = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
  try:
    temp.bind(('localhost', 0))
    port = temp.getsockname()[1]
  finally:
    temp.close()
  return port


def with_app(app):
  """Decorator for associating individual tests with a WSGI application.

  Used with WsgiTest to associate an individual WSGI test with a provided
  application.

  See WsgiTest for information about how to test a WSGI application.

  Example:

    def my_application(environ, start_response):
      ...

    class MyTest(WsgiTest):

      @with_app(my_application)
      def test_my_app(self):
        ...

  Returns:
    Decorator used to decorate a test method.
  """
  def with_app_decorator(method):
    method.app = app
    return method
  return with_app_decorator


class WsgiTest(unittest.TestCase):
  """Base class for doing WSGI applicaiton tests.

  Optionally sets up an entire server so that tests can be run from the point
  of view of an HTTP client.

  To set up a test for a specific applicaiton, override create_wsgi_app function.
  or replace with a static method factory function.
  """

  # How long in seconds to wait for server to start.
  START_DELAY_TIME = 0.5

  def setUp(self):
    if sys.version_info[:2] < (2, 6):
      print >>sys.stderr, ('WsgiTest requires Python version 2.6 or greater. '
                           'Current version is %d.%d' % sys.version_info[:2])
      sys.exit(1)
    
    self.app = self.create_wsgi_app()
    self.server = None
    if self.app:
      self.validated_app = validate.validator(self.app)
      self.port = pick_unused_port()
      self.server = simple_server.make_server(
        'localhost', self.port, self.validated_app)
      wait_for_start = threading.Event()
      def starter():
        wait_for_start.set()
        self.server.serve_forever()
      self.server_thread = threading.Thread(target=starter)
      self.server_thread.start()
      wait_for_start.wait()
      # Seems to be necessary to sleep for a while to give server time to
      # start.
      time.sleep(self.START_DELAY_TIME)
      self.connection = httplib.HTTPConnection('localhost', self.port)

  def tearDown(self):
    if self.server:
      self.server.shutdown()
      self.server_thread.join()

  def do_request(self):
    """Does a basic request against local server.

    Only use if server has been initialized on test.
    """
    self.connection.request('GET', '/')
    return self.connection.getresponse()

  def create_wsgi_app(self):
    """Create WSGI application for use with server in test.

    If test method has been decorated using 'with_app', will pass that
    application to the test server.

    If no association is found, will check TEST_APP class attribute.

    Override this method to have more complex behavior.

    Returns:
      A WSGI application if method has app attribute or test has TEST_APP
      class attribute, else None.  If None, no server is started on the test.
    """
    method_name = self.id().split('.')[-1]
    method = getattr(self, method_name)
    app = getattr(method, 'app', None)
    if not app:
      app = getattr(self, 'TEST_APP', None)
    return app


class TestCase(unittest.TestCase):
  """Base class for additional testing functionality."""

  def assertIs(self, a, b, message=None):
    """Assert that two values are actually the same.

    Args:
      a: First value to compare.
      b: Second value to compare.
      message: Optional message.
    """
    message = message or ('Expected %r, was %r' % (a, b))
    self.assertTrue(a is b, message)
