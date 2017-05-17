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
import re
import os
import unittest
import doctest

import zope.component.testing
from zope.configuration import xmlconfig
from zope.interface import implementer
from zope.traversing.interfaces import IContainmentRoot
from zope.location import LocationProxy

from zope.testing import renormalizing

import zope.testing.module

from webtest import TestApp

from zope.app.apidoc.apidoc import APIDocumentation
from zope.app.apidoc.testing import APIDocLayer

from zope.app.component.testing import PlacefulSetup, setUpTraversal

_old_appsetup_context = None

def _setUp_AppSetup(filename='configure.zcml', execute=False):
    config_file = os.path.join(
        os.path.dirname(zope.app.apidoc.__file__), filename)

    # # Fix up path for tests.
    global _old_appsetup_context
    _old_appsetup_context = zope.app.appsetup.appsetup.getConfigContext()
    zope.app.appsetup.appsetup.__config_context = xmlconfig.file(
        config_file, zope.app.apidoc, execute=execute)

def _tearDown_AppSetup():
    global _old_appsetup_context
    zope.app.appsetup.appsetup.__config_context = _old_appsetup_context
    _old_appsetup_context = None



def _setUp_LayerPlace(test):
    # We're in the layer, so we don't want to tear down zope.testing,
    # which would tear down zope.component
    root_folder = PlacefulSetup().buildFolders(True)
    setUpTraversal()

    global _old_appsetup_context
    _old_appsetup_context = zope.app.appsetup.appsetup.getConfigContext()
    zope.app.appsetup.appsetup.__config_context = APIDocLayer.context


    # Set up apidoc module
    test.globs['apidoc'] = APIDocumentation(root_folder, '++apidoc++')
    test.globs['rootFolder'] = root_folder


def _tearDown_LayerPlace(test):
    _tearDown_AppSetup()


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
    xmlconfig.file('configure.zcml', zope.app.renderer)
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

standard_checker_patterns = (
    (re.compile(r"u('[^']*')"), r"\1"),
    (re.compile(r"b('[^']*')"), r"\1"),
    (re.compile("__builtin__"), 'builtins'),
    # repr of old style class is different on py2
    (re.compile("<class zope.app.apidoc.doctest.B.*>"),
     "<class 'zope.app.apidoc.doctest.B'>"),
    # there are no unbound methods on python 3
    (re.compile("<unbound method ([^>]*)>"),
     r"<function \1 at 0xabc>")
)

def standard_checker(*extra_patterns):
    return renormalizing.RENormalizing(standard_checker_patterns + extra_patterns)

standard_option_flags = (doctest.NORMALIZE_WHITESPACE
                         | doctest.ELLIPSIS
                         | renormalizing.IGNORE_EXCEPTION_MODULE_IN_PYTHON2)

def LayerDocFileSuite(filename, package):
    test = doctest.DocFileSuite(
        filename,
        package=package,
        setUp=_setUp_LayerPlace,
        tearDown=_tearDown_LayerPlace,
        checker=standard_checker(),
        optionflags=standard_option_flags)
    test.layer = APIDocLayer
    return test

def LayerDocTestSuite(modulename):
    test = doctest.DocTestSuite(
        modulename,
        setUp=_setUp_LayerPlace,
        tearDown=_tearDown_LayerPlace,
        checker=standard_checker(),
        optionflags=standard_option_flags)
    test.layer = APIDocLayer
    return test

def test_suite():
    checker = standard_checker()

    def file_test(name, **kwargs):
        return doctest.DocFileSuite(
            name,
            setUp=setUp,
            tearDown=tearDown,
            checker=checker,
            optionflags=standard_option_flags,
            **kwargs)

    return unittest.TestSuite((
        doctest.DocTestSuite('zope.app.apidoc.browser.apidoc',
                             setUp=setUp, tearDown=tearDown),
        file_test('README.rst'),
        file_test('classregistry.rst'),
        file_test('interface.rst'),
        file_test('component.rst'),
        file_test('presentation.rst',
                  globs={'__file__': __file__}),
        file_test('utilities.rst'),
    ))

if __name__ == '__main__':
    unittest.main(defaultTest="test_suite")
