##############################################################################
#
# Copyright (c) 2004 Zope Foundation and Contributors.
# All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
##############################################################################
"""Tests for the Interface Documentation Module

"""
from __future__ import absolute_import
import os
import unittest
import doctest

import zope.component.testing
from zope.configuration import xmlconfig
# from zope.component.interfaces import IFactory
from zope.interface import implementer
from zope.traversing.interfaces import IContainmentRoot
from zope.location import LocationProxy


# from zope.app.renderer.rest import ReStructuredTextSourceFactory
# from zope.app.renderer.rest import IReStructuredTextSource
# from zope.app.renderer.rest import ReStructuredTextToHTMLRenderer

import zope.testing.module

from webtest import TestApp


def _setUp_AppSetup():
    config_file = os.path.join(
        os.path.dirname(zope.app.apidoc.__file__), 'configure.zcml')

    # # Fix up path for tests.
    global old_context
    old_context = zope.app.appsetup.appsetup.getConfigContext()
    zope.app.appsetup.appsetup.__config_context = xmlconfig.file(
        config_file, zope.app.apidoc, execute=False)

def _tearDown_AppSetup():
    zope.app.appsetup.appsetup.__config_context = old_context


class BrowserTestCase(unittest.TestCase):

    def setUp(self):
        super(BrowserTestCase, self).setUp()
        _setUp_AppSetup()
        self._testapp = TestApp(self.layer.make_wsgi_app())

    def tearDown(self):
        _tearDown_AppSetup()
        super(BrowserTestCase, self).tearDown()


    def checkForBrokenLinks(self, orig_response, path, basic=None):
        response = self.publish(path, basic=basic)
        links = response.html.find_all('a')

        for link in links:
            try:
                href = link.attrs['href']
            except KeyError:
                pass
            if '++apidoc++' in href:
                # XXX: We are this! Enable it
                # We don't install this at test time
                continue
            if href.startswith('http://dev.zope.org'):
                # Don't try to follow external links
                continue
            if href.startswith('./'):
                href = href[2:]

            if not href.startswith('/'):
                href = path.rsplit('/', 1)[0] + '/' + href
            self.publish(href, basic=basic)

    def publish(self, path, basic=None, form=None, headers=None, env=None):
        assert basic
        self._testapp.authorization = ('Basic', tuple(basic.split(':')))
        env = env or {}
        env['wsgi.handleErrors'] = False
        if form:
            response = self._testapp.post(path, params=form,
                                          extra_environ=env, headers=headers)
        else:
            response = self._testapp.get(path, extra_environ=env, headers=headers)

        response.getBody = lambda: response.unicode_normal_body
        response.getStatus = lambda: response.status_int
        response.getHeader = lambda n: response.headers[n]
        return response



def setUp(test):
    import zope.app.renderer
    zope.component.testing.setUp()
    # Register Renderer Components
    xmlconfig.file('configure.zcml', zope.app.renderer)
    # ztapi.provideUtility(IFactory, ReStructuredTextSourceFactory,
    #                      'zope.source.rest')
    # ztapi.browserView(IReStructuredTextSource, '',
    #                   ReStructuredTextToHTMLRenderer)
    # # Cheat and register the ReST renderer as the STX one as well.
    # ztapi.provideUtility(IFactory, ReStructuredTextSourceFactory,
    #                      'zope.source.stx')
    # ztapi.browserView(IReStructuredTextSource, '',
    #                   ReStructuredTextToHTMLRenderer)
    zope.testing.module.setUp(test, 'zope.app.apidoc.doctest')


def tearDown(test):
    zope.component.testing.tearDown()
    zope.testing.module.tearDown(test, 'zope.app.apidoc.doctest')

# Generally useful classes and functions

@implementer(IContainmentRoot)
class Root(object):

    __parent__ = None
    __name__ = ''

def rootLocation(obj, name):
    return LocationProxy(obj, Root(), name)


def test_suite():
    return unittest.TestSuite((
        doctest.DocTestSuite('zope.app.apidoc.browser.apidoc',
                             setUp=setUp, tearDown=tearDown),
        doctest.DocFileSuite('README.rst',
                             setUp=setUp,
                             tearDown=tearDown,
                             optionflags=doctest.NORMALIZE_WHITESPACE),
        doctest.DocFileSuite('classregistry.rst',
                             optionflags=doctest.NORMALIZE_WHITESPACE),
        doctest.DocFileSuite('interface.rst',
                             setUp=setUp,
                             tearDown=tearDown,
                             optionflags=doctest.NORMALIZE_WHITESPACE),
        doctest.DocFileSuite('component.rst',
                             setUp=setUp,
                             tearDown=tearDown,
                             optionflags=doctest.NORMALIZE_WHITESPACE),
        doctest.DocFileSuite('presentation.rst',
                             setUp=zope.component.testing.setUp,
                             tearDown=zope.component.testing.tearDown,
                             optionflags=doctest.NORMALIZE_WHITESPACE,
                             globs={'__file__': __file__}),
        doctest.DocFileSuite('utilities.rst',
                             setUp=setUp,
                             tearDown=tearDown,
                             optionflags=doctest.NORMALIZE_WHITESPACE),
    ))

if __name__ == '__main__':
    unittest.main(defaultTest="test_suite")
