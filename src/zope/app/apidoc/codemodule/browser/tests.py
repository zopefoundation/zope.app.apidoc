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
"""Tests for the Code Documentation Module

"""
import unittest

from zope.app.apidoc.testing import APIDocLayer
from zope.app.apidoc.tests import BrowserTestCase
from zope.app.apidoc.tests import LayerDocFileSuite
from zope.app.apidoc.tests import LayerDocTestSuite

import zope.app.apidoc.codemodule


def foo(cls, bar=1, *args): # used in README.rst
    """This is the foo function."""
foo.deprecated = True


class CodeModuleTests(BrowserTestCase):
    """Just a couple of tests ensuring that the templates render."""
    layer = APIDocLayer

    def testMenu(self):
        response = self.publish('/++apidoc++/Code/menu.html',
                                basic='mgr:mgrpw')
        self.assertEqual(response.getStatus(), 200)
        body = response.getBody()
        self.assertIn('Zope Source', body)
        self.checkForBrokenLinks(body, '/++apidoc++/Code/menu.html',
                                 basic='mgr:mgrpw')

    def testMenuCodeFinder(self):
        response = self.publish('/++apidoc++/Code/menu.html',
                                basic='mgr:mgrpw',
                                form={'path': 'Code', 'SUBMIT': 'Find'})
        self.assertEqual(response.getStatus(), 200)
        body = response.getBody()
        self.assertIn(
            'zope.app.apidoc.codemodule.codemodule.CodeModule', body)
        self.checkForBrokenLinks(body, '/++apidoc++/Code/menu.html',
                                 basic='mgr:mgrpw')

    def testModuleDetailsView(self):
        response = self.publish('/++apidoc++/Code/zope/app/apidoc/apidoc',
                                basic='mgr:mgrpw')
        self.assertEqual(response.getStatus(), 200)
        body = response.getBody()
        self.assertIn('Zope 3 API Documentation', body)
        self.checkForBrokenLinks(
            body, '/++apidoc++/Code/zope/app/apidoc/apidoc', basic='mgr:mgrpw')

    def testClassDetailsView(self):
        response = self.publish(
            '/++apidoc++/Code/zope/app/apidoc/apidoc/APIDocumentation',
            basic='mgr:mgrpw')
        self.assertEqual(response.getStatus(), 200)
        body = response.getBody()
        self.assertIn('Represent the complete API Documentation.', body)
        self.checkForBrokenLinks(
            body, '/++apidoc++/Code/zope/app/apidoc/apidoc/APIDocumentation',
            basic='mgr:mgrpw')

    def testFunctionDetailsView(self):
        response = self.publish(
            '/++apidoc++/Code/zope/app/apidoc/apidoc/handleNamespace',
            basic='mgr:mgrpw')
        self.assertEqual(response.getStatus(), 200)
        body = response.getBody()
        self.assertIn('handleNamespace(ob, name)', body)
        self.checkForBrokenLinks(
             body,
            '/++apidoc++/Code/zope/app/apidoc/apidoc/handleNamespace',
             basic='mgr:mgrpw')

    def testTextFileDetailsView(self):
        response = self.publish(
            '/++apidoc++/Code/zope/app/apidoc/README.rst/index.html',
            basic='mgr:mgrpw')
        self.assertEqual(response.getStatus(), 200)
        body = response.getBody()
        self.checkForBrokenLinks(
            body, '/++apidoc++/Code/zope/app/apidoc/README.rst/index.html',
            basic='mgr:mgrpw')

    def testZCMLFileDetailsView(self):
        response = self.publish(
            '/++apidoc++/Code/zope/app/apidoc/configure.zcml/index.html',
            basic='mgr:mgrpw')
        self.assertEqual(response.getStatus(), 200)
        body = response.getBody()
        self.checkForBrokenLinks(
            body, '/++apidoc++/Code/zope/app/apidoc/configure.zcml/index.html',
            basic='mgr:mgrpw')


def test_suite():
    return unittest.TestSuite((
        LayerDocFileSuite(
            'README.rst',
            zope.app.apidoc.codemodule.browser),
        LayerDocTestSuite(
            'zope.app.apidoc.codemodule.browser.menu'),
        LayerDocFileSuite(
            "introspector.rst",
            zope.app.apidoc.codemodule.browser),
        unittest.defaultTestLoader.loadTestsFromName(__name__),
    ))

if __name__ == '__main__':
    unittest.main()
