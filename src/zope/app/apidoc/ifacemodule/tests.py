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

import unittest

import zope.app.apidoc.ifacemodule

from zope.app.apidoc.testing import APIDocLayer
from zope.app.apidoc.tests import LayerDocFileSuite
from zope.app.apidoc.tests import BrowserTestCase


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

    def testStaticMenu(self):
        response = self.publish(
            '/++apidoc++/Interface/staticmenu.html',
            basic='mgr:mgrpw')

        self.assertEqual(response.getStatus(), 200)
        body = response.getBody()
        self.assertIn(
            'zope.app.apidoc.interfaces.IDocumentationModule', body)
        self.checkForBrokenLinks(body, '/++apidoc++/Interface/staticmenu.html',
                                 basic='mgr:mgrpw',
                                 # This page is slow, only do a few
                                 max_links=5)


def test_suite():

    readme = LayerDocFileSuite(
        'README.rst',
        zope.app.apidoc.ifacemodule)

    browser = LayerDocFileSuite(
        'browser.rst',
        zope.app.apidoc.ifacemodule)

    return unittest.TestSuite((
        readme,
        browser,
        unittest.defaultTestLoader.loadTestsFromName(__name__)
    ))
