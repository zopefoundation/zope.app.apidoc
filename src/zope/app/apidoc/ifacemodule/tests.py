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
import unittest
import doctest

from zope.app.component.testing import PlacefulSetup, setUpTraversal

from zope.app.apidoc.testing import APIDocLayer
from zope.app.apidoc.apidoc import APIDocumentation

from zope.app.apidoc.ifacemodule.ifacemodule import InterfaceModule
from zope.app.apidoc.tests import BrowserTestCase

from zope.testing import renormalizing

def setUp(test):
    root_folder = PlacefulSetup().buildFolders(True)
    setUpTraversal()

    # Set up apidoc module
    test.globs['apidoc'] = APIDocumentation(root_folder, '++apidoc++')


def tearDown(test):
    pass


class InterfaceModuleTests(BrowserTestCase):
    """Just a couple of tests ensuring that the templates render."""

    layer = APIDocLayer

    def testMenu(self):
        response = self.publish(
            '/++apidoc++/Interface/menu.html',
            basic='mgr:mgrpw',
            env={'name_only': 'True', 'search_str': 'IDoc'})
        self.assertEqual(response.getStatus(), 200)
        body = response.getBody()
        self.assertIn(
            'zope.app.apidoc.interfaces.IDocumentationModule', body)
        self.checkForBrokenLinks(body, '/++apidoc++/Interface/menu.html',
                                 basic='mgr:mgrpw')

    def testInterfaceDetailsView(self):
        response = self.publish(
            '/++apidoc++/Interface'
            '/zope.app.apidoc.ifacemodule.ifacemodule.IInterfaceModule'
            '/index.html',
            basic='mgr:mgrpw')
        self.assertEqual(response.getStatus(), 200)
        body = response.getBody()
        self.assertIn('Interface API Documentation Module', body)
        self.assertIn('/++apidoc++/Code/zope/app/apidoc'
                      '/ifacemodule/ifacemodule/index.html', body)


def test_suite():
    checker = renormalizing.RENormalizing([
        (re.compile(r"u('[^']*')"), r"\1"),
        (re.compile("__builtin__"), 'builtins'),
        (re.compile(r"b('[^']*')"), r"\1"),
    ])

    readme = doctest.DocFileSuite(
        'README.rst',
        setUp=setUp,
        tearDown=tearDown,
        checker=checker,
        optionflags=(doctest.NORMALIZE_WHITESPACE
                     | doctest.ELLIPSIS
                     | renormalizing.IGNORE_EXCEPTION_MODULE_IN_PYTHON2))
    readme.layer = APIDocLayer
    browser = doctest.DocFileSuite(
        'browser.rst',
        setUp=setUp,
        tearDown=tearDown,
        checker=checker,
        optionflags=(doctest.NORMALIZE_WHITESPACE
                     | doctest.ELLIPSIS
                     | renormalizing.IGNORE_EXCEPTION_MODULE_IN_PYTHON2))
    browser.layer = APIDocLayer
    return unittest.TestSuite((
        readme,
        browser,
        unittest.defaultTestLoader.loadTestsFromName(__name__)
    ))

if __name__ == '__main__':
    unittest.main(defaultTest="test_suite")
