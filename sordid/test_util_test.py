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
from wsgiref import util as wsgi_util

from sordid import test_util


def define_test_app(message):
  """Create a simple test application with custom message"""
  def test_app(environ, start_response):
    response_headers = [('content-type', 'text/plain')]
    for name, value in environ.items():
      if name.startswith('HTTP_'):
        header_name = name[len('HTTP_'):].lower().replace('_', '-')
        if header_name.startswith('header'):
          response_headers.append((header_name, 'echo: ' + value))
    start_response('200 OK', response_headers)
    response_string = '\n'.join(['Uri: %s' % wsgi_util.request_uri(environ),
                                 'Method: %s' % environ['REQUEST_METHOD'],
                                message])
    return [str.encode(response_string)]
  return test_app


class WsgiTestTest(test_util.WsgiTest):

  TEST_APP = staticmethod(define_test_app('class-attribute'))

  def test_server_up(self):
    self.connection.request('POST', '/some_path', 'body',
                            {'header-1': 'a-value'})
    response = self.connection.getresponse()
    self.assertEquals('echo: a-value', response.getheader('header-1'))
    self.assertEquals(str.encode('Uri: http://localhost:%d/some_path\n'
                                 'Method: POST\n'
                                 'class-attribute' %
                                 self.port),
                      response.read())

  @test_util.with_app(define_test_app('from-with-app'))
  def test_with_app(self):
    self.connection.request('POST', '/some_path', 'body',
                            {'header-1': 'a-value'})
    response = self.connection.getresponse()
    self.assertEquals('echo: a-value', response.getheader('header-1'))
    self.assertEquals(str.encode('Uri: http://localhost:%d/some_path\n'
                                 'Method: POST\n'
                                 'from-with-app' %
                                 self.port),
                      response.read())


if __name__ == '__main__':
  unittest.main()
