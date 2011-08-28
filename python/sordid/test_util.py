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


class WsgiTest(unittest.TestCase):
  """Base class for doing WSGI applicaiton tests.

  Sets up an entire server so that tests can be run from the point of view
  of an HTTP client.

  To set up a test for a specific applicaiton, override create_wsgi_app function.
  or replace with a static method factory function.
  """

  def setUp(self):
    if sys.version_info[:2] < (2, 6):
      print >>sys.stderr, ('WsgiTest requires Python version 2.6 or greater. '
                           'Current version is %d.%d' % sys.version_info[:2])
      sys.exit(1)
    
    self.app = self.create_wsgi_app()
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
    time.sleep(1)
    self.connection = httplib.HTTPConnection('localhost', self.port)

  def tearDown(self):
    self.server.shutdown()
    self.server_thread.join()

  def create_wsgi_app(self):
    raise NotImplememtnedError()
