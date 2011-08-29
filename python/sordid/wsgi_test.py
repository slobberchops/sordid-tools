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

from sordid import test_util
from sordid import wsgi


class StaticServerTest(test_util.WsgiTest):

  def do_request(self):
    self.connection.request('GET', '/')
    return self.connection.getresponse()

  @test_util.with_app(wsgi.static(content='This is content'))
  def test_basic_content(self):
    response = self.do_request()
    self.assertEquals(200, response.status)
    self.assertEquals('OK', response.reason)
    self.assertEquals('text/html', response.getheader('content-type'))
    self.assertEquals('This is content', response.read())

  @test_util.with_app(wsgi.static(content='This is content',
                                  content_type='text/plain'))
  def test_other_content_type(self):
    response = self.do_request()
    self.assertEquals(200, response.status)
    self.assertEquals('OK', response.reason)
    self.assertEquals('text/plain', response.getheader('content-type'))
    self.assertEquals('This is content', response.read())

  @test_util.with_app(wsgi.static(404))
  def test_integer_status(self):
    response = self.do_request()
    self.assertEquals(404, response.status)
    self.assertEquals('Not Found', response.reason)
    self.assertEquals('text/html', response.getheader('content-type'))
    self.assertEquals('', response.read())

  @test_util.with_app(wsgi.static('500 Some Kind Of Error'))
  def test_string_status(self):
    response = self.do_request()
    self.assertEquals(500, response.status)
    self.assertEquals('Some Kind Of Error', response.reason)
    self.assertEquals('text/html', response.getheader('content-type'))
    self.assertEquals('', response.read())

  @test_util.with_app(wsgi.static((400, 'Bad Something')))
  def test_tuple_status(self):
    response = self.do_request()
    self.assertEquals(400, response.status)
    self.assertEquals('Bad Something', response.reason)
    self.assertEquals('text/html', response.getheader('content-type'))
    self.assertEquals('', response.read())

  @test_util.with_app(wsgi.static(headers={'header-1': 'value-1',
                                           'header-2': 'value-2'}))
  def test_dict_headers(self):
    response = self.do_request()
    self.assertEquals(200, response.status)
    self.assertEquals('OK', response.reason)
    self.assertEquals('text/html', response.getheader('content-type'))
    self.assertEquals('value-1', response.getheader('header-1'))
    self.assertEquals('value-2', response.getheader('header-2'))
    self.assertEquals('', response.read())

  @test_util.with_app(wsgi.static(headers=[('header-1', 'value-1'),
                                           ('header-2', 'value-2')]))
  def test_list_headers(self):
    response = self.do_request()
    self.assertEquals(200, response.status)
    self.assertEquals('OK', response.reason)
    self.assertEquals('text/html', response.getheader('content-type'))
    self.assertEquals('value-1', response.getheader('header-1'))
    self.assertEquals('value-2', response.getheader('header-2'))
    self.assertEquals('', response.read())


if __name__ == '__main__':
  unittest.main()
