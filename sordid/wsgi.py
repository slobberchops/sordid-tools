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

import logging
import httplib

from sordid import util

NEXT_APP_ENVIRON = 'sordid.next.app'


@util.positional(2)
def static(code=200, content='', headers={},
           content_type='text/html'):
  """Static content application.

  This application serves up the same static content every time it is
  called, regardless of any request parameters or path information.

  Args:
    code: Response code to send.  Can be an integer, a string or a pair
      (code, message).  If string, no parsing or checking occurs.
    content: Byte-string to send as response.
    headers: Additional headers to send in response.
    content_type: Content-type of response.
  """
  if isinstance(code, (int, long)):
    code = '%d %s' % (code, httplib.responses.get(code, 'Unknown Status'))
  elif not isinstance(code, basestring):
    code = '%d %s' % code

  if isinstance(headers, dict):
    headers = headers.items()

  headers.append(('content-type', content_type))

  if isinstance(content, basestring):
    content = (content,)
  else:
    content = tuple(content)

  def response_app(environ, start_response):
    start_response(code, headers)
    return content
  return response_app


def _define_standard_responses():
  """Configures global applications for HTTP response codes.

  This function initializes global variables and is deleted after executed.

  See for list in code for list of definitions.  All variables defined begin
  with 'HTTP_'.  For example:

    HTTP_BAD_REQUEST
    HTTP_SERVER_ERROR
  """
  for name in ('CONTINUE',
               'SWITCHING_PROTOCOLS',
               'PROCESSING',
               'OK',
               'CREATED',
               'ACCEPTED',
               'NON_AUTHORITATIVE_INFORMATION',
               'NO_CONTENT',
               'RESET_CONTENT',
               'PARTIAL_CONTENT',
               'MULTI_STATUS',
               'IM_USED',
               'MULTIPLE_CHOICES',
               'MOVED_PERMANENTLY',
               'FOUND',
               'SEE_OTHER',
               'NOT_MODIFIED',
               'USE_PROXY',
               'TEMPORARY_REDIRECT',
               'BAD_REQUEST',
               'UNAUTHORIZED',
               'PAYMENT_REQUIRED',
               'FORBIDDEN',
               'NOT_FOUND',
               'METHOD_NOT_ALLOWED',
               'NOT_ACCEPTABLE',
               'PROXY_AUTHENTICATION_REQUIRED',
               'REQUEST_TIMEOUT',
               'CONFLICT',
               'GONE',
               'LENGTH_REQUIRED',
               'PRECONDITION_FAILED',
               'REQUEST_ENTITY_TOO_LARGE',
               'REQUEST_URI_TOO_LONG',
               'UNSUPPORTED_MEDIA_TYPE',
               'REQUESTED_RANGE_NOT_SATISFIABLE',
               'EXPECTATION_FAILED',
               'UNPROCESSABLE_ENTITY',
               'LOCKED',
               'FAILED_DEPENDENCY',
               'UPGRADE_REQUIRED',
               'INTERNAL_SERVER_ERROR',
               'NOT_IMPLEMENTED',
               'BAD_GATEWAY',
               'SERVICE_UNAVAILABLE',
               'GATEWAY_TIMEOUT',
               'HTTP_VERSION_NOT_SUPPORTED',
               'INSUFFICIENT_STORAGE',
               'NOT_EXTENDED',
               ):
    code = getattr(httplib, name)
    description = httplib.responses.get(code, None)
    if description is None:
      splitted = (part.capitalize() for part in name.split('_'))
      description = ' '.join(splitted)
    globals()['HTTP_' + name] = static((code, description))
_define_standard_responses()
del _define_standard_responses


def choose(*apps):
  """Chose from multiple WSGI applications.

  Chains multiple applications together so that the first application
  encountered that the result of the first application that does not send
  404 as it's status is sent to the client.  Any application in the list
  after the first successful application is not executed.
  """
  if len(apps) < 2:
    raise TypeError('Choose function requires at least two applications')

  def choose_app(environ, start_response):
    started = [False]
    def choose_start_response(status, headers):
      if not status.startswith('404'):
        started[0] = True
        start_response(status, headers)

    for app in apps:
      content = app(environ, choose_start_response)
      if started[0]:
        return content

    return HTTP_NOT_FOUND(environ, start_response)
  return choose_app
      

def chain(*apps):
  """Chain middleware applications together.

  Modifies each applications executing environment to contain a reference to
  the next middleware application in the chain.  The next middleware application
  can be accessed via 'sordid.next.app'.
  """
  if len(apps) < 2:
    raise TypeError('Chain function requires at least two applications')

  def make_chain(apps):
    previous_app = apps[0]
    if len(apps) == 1:
      next_app = None
    else:
      next_app = make_chain(apps[1:])
    def chained_app(environ, start_response):
      environ[NEXT_APP_ENVIRON] = next_app
      try:
        return previous_app(environ, start_response)
      finally:
        environ[NEXT_APP_ENVIRON] = previous_app
    return chained_app
  return make_chain(apps)

