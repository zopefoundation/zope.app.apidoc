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
"""Tests for the ZCML Documentation Module

"""
import re
import os
import unittest
import doctest

from zope.configuration import xmlconfig

from zope.testing import renormalizing
import zope.app.appsetup.appsetup

from zope import component as ztapi
import zope.traversing
import zope.app.tree
import zope.security
import zope.browserresource
import zope.browserpage
import zope.location


from zope.app.component.testing import PlacefulSetup

import zope.app.apidoc
from zope.app.apidoc.testing import APIDocLayer
from zope.app.apidoc.tests import Root
from zope.app.apidoc.tests import BrowserTestCase
from zope.app.apidoc.apidoc import APIDocumentation
from zope.app.apidoc.interfaces import IDocumentationModule
from zope.app.apidoc.zcmlmodule import Namespace, Directive
from zope.app.apidoc.zcmlmodule import ZCMLModule

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

def setUp(test):
    root_folder = PlacefulSetup().setUp(True, True)

    ctx = xmlconfig.file('meta.zcml', zope.security)
    ctx = xmlconfig.file('meta.zcml', ztapi, context=ctx)
    ctx = xmlconfig.file('meta.zcml', zope.browserresource, context=ctx)
    ctx = xmlconfig.file('meta.zcml', zope.browserpage, context=ctx)
    ctx = xmlconfig.file('configure.zcml', zope.location, context=ctx)
    ctx = xmlconfig.file('configure.zcml', zope.traversing, context=ctx)
    ctx = xmlconfig.file('configure.zcml', zope.security, context=ctx)
    xmlconfig.file('configure.zcml', zope.app.tree, context=ctx)

    # Set up apidoc module
    test.globs['apidoc'] = APIDocumentation(root_folder, '++apidoc++')

    # Register documentation modules
    ztapi.provideUtility(ZCMLModule(), IDocumentationModule,'ZCML')

    _setUp_AppSetup()

def tearDown(test):
    PlacefulSetup().tearDown()
    _tearDown_AppSetup()
    from zope.app.apidoc import zcmlmodule
    zcmlmodule.namespaces = None
    zcmlmodule.subdirs = None

def getDirective():
    module = ZCMLModule()
    module.__parent__ = Root()
    module.__name__ = 'ZCML'

    def foo(): pass

    ns = Namespace(module, 'http://namespaces.zope.org/browser')
    return Directive(ns, 'page', None, foo, None, ())


class ZCMLModuleTests(BrowserTestCase):
    """Just a couple of tests ensuring that the templates render."""
    layer = APIDocLayer

    def setUp(self):
        super(ZCMLModuleTests, self).setUp()
        _setUp_AppSetup()

    def tearDown(self):
        _tearDown_AppSetup()
        super(ZCMLModuleTests, self).tearDown()

    def testMenu(self):
        response = self.publish(
            '/++apidoc++/ZCML/menu.html',
            basic='mgr:mgrpw')
        self.assertEqual(response.getStatus(), 200)
        body = response.getBody()
        self.assertIn('All Namespaces', body)
        self.checkForBrokenLinks(body, '/++apidoc++/ZCML/menu.html',
                                 basic='mgr:mgrpw')

    def testDirectiveDetailsView(self):
        response = self.publish('/++apidoc++/ZCML/ALL/configure/index.html',
                                basic='mgr:mgrpw')
        self.assertEqual(response.getStatus(), 200)
        body = response.getBody()
        self.assertIn('<i>all namespaces</i>', body)
        self.checkForBrokenLinks(body,
                                 '/++apidoc++/ZCML/ALL/configure/index.html',
                                 basic='mgr:mgrpw')


def test_suite():
    checker = renormalizing.RENormalizing([
        (re.compile(r"u('[^']*')"), r"\1"),
        (re.compile("__builtin__"), 'builtins'),
    ])
    return unittest.TestSuite((
        doctest.DocFileSuite('README.rst',
                             setUp=setUp, tearDown=tearDown,
                             optionflags=doctest.NORMALIZE_WHITESPACE,
                             checker=checker),
        doctest.DocFileSuite('browser.rst',
                             setUp=setUp, tearDown=tearDown,
                             optionflags=doctest.NORMALIZE_WHITESPACE,
                             checker=checker),
        unittest.defaultTestLoader.loadTestsFromName(__name__),
    ))

if __name__ == '__main__':
    unittest.main(default='test_suite')
