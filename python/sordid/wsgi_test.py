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


class ChooseTest(test_util.WsgiTest):

  @test_util.with_app(wsgi.choose(
    wsgi.static(400, 'first', headers={'a': '1'}),
    wsgi.static(500, 'second', headers={'a': '2'}),
    wsgi.static(300, 'third', headers={'a': '3'})))
  def test_match_first(self):
    response = self.do_request()
    self.assertEquals(400, response.status)
    self.assertEquals('first', response.read())
    self.assertEquals('1', response.getheader('a'))

  @test_util.with_app(wsgi.choose(
    wsgi.static(404, 'first', headers={'a': '1'}),
    wsgi.static(500, 'second', headers={'a': '2'}),
    wsgi.static(300, 'third', headers={'a': '3'})))
  def test_match_second(self):
    response = self.do_request()
    self.assertEquals(500, response.status)
    self.assertEquals('second', response.read())
    self.assertEquals('2', response.getheader('a'))

  @test_util.with_app(wsgi.choose(
    wsgi.static(404, 'first', headers={'a': '1'}),
    wsgi.static(404, 'second', headers={'a': '2'}),
    wsgi.static(300, 'third', headers={'a': '3'})))
  def test_match_third(self):
    response = self.do_request()
    self.assertEquals(300, response.status)
    self.assertEquals('third', response.read())
    self.assertEquals('3', response.getheader('a'))

  def test_no_apps(self):
    try:
      wsgi.choose()
    except TypeError, err:
      self.assertEquals('Choose function requires at least two applications',
                        str(err))
    else:
      self.fail('choose should require at least two applications')

  def test_only_one_app(self):
    try:
      wsgi.choose(wsgi.HTTP_INTERNAL_SERVER_ERROR)
    except TypeError, err:
      self.assertEquals('Choose function requires at least two applications',
                        str(err))
    else:
      self.fail('choose should require at least two applications')


def chained(name):
  """Create a simple chain tester that calls next application in chain."""
  def chained_app(environ, start_response):
    next_app = environ[wsgi.NEXT_APP_ENVIRON]
    if next_app:
      content = next_app(environ, start_response)
    else:
      content = []
      start_response('200 OK', [('content-type', 'text/plain')])
    return content + [name + ' ']
  return chained_app


class ChainTest(test_util.WsgiTest):

  @test_util.with_app(wsgi.chain(chained('app1'),
                                 chained('app2'),
                                 chained('app3')))
  def test_chain(self):
    response = self.do_request()
    self.assertEquals(200, response.status)
    self.assertEquals('app3 app2 app1 ', response.read())

  def test_no_apps(self):
    try:
      wsgi.chain()
    except TypeError, err:
      self.assertEquals('Chain function requires at least two applications',
                        str(err))
    else:
      self.fail('chain should require at least two applications')

  def test_only_one_app(self):
    try:
      wsgi.chain(wsgi.HTTP_INTERNAL_SERVER_ERROR)
    except TypeError, err:
      self.assertEquals('Chain function requires at least two applications',
                        str(err))
    else:
      self.fail('chain should require at least two applications')


if __name__ == '__main__':
  unittest.main()
