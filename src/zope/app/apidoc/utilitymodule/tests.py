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
"""Tests for the Utility Documentation Module

"""

import unittest

import zope.deprecation

from zope.app.apidoc.testing import APIDocLayer

from zope.app.apidoc.tests import BrowserTestCase
from zope.app.apidoc.tests import LayerDocFileSuite
import zope.app.apidoc.utilitymodule


class UtilityModuleTests(BrowserTestCase):
    """Just a couple of tests ensuring that the templates render."""

    layer = APIDocLayer

    def testMenu(self):
        response = self.publish(
            '/++apidoc++/Utility/menu.html',
            basic='mgr:mgrpw')
        self.assertEqual(response.getStatus(), 200)
        body = response.getBody()
        self.assertIn('IDocumentationModule', body)

        # BBB 2006/02/18, to be removed after 12 months
        # this avoids the deprecation warning for the deprecated
        # zope.publisher.interfaces.ILayer interface which get traversed
        # as a utility in this test
        # This is slow, so we limit the number of links we fetch.
        zope.deprecation.__show__.off()
        self.checkForBrokenLinks(body, '/++apidoc++/Utility/menu.html',
                                 basic='mgr:mgrpw',
                                 max_links=10)
        zope.deprecation.__show__.on()

    def testUtilityDetailsView(self):
        response = self.publish(
            '/++apidoc++/Utility/'
            'zope.app.apidoc.interfaces.IDocumentationModule/'
            'Utility/index.html',
            basic='mgr:mgrpw')
        self.assertEqual(response.getStatus(), 200)
        body = response.getBody()
        self.assertIn(
            'zope.app.apidoc.utilitymodule.utilitymodule.UtilityModule',
            body)
        self.checkForBrokenLinks(
            body,
            '/++apidoc++/Utility/'
            'zope.app.apidoc.interfaces.IDocumentationModule/'
            'Utility/index.html',
            basic='mgr:mgrpw')


def test_suite():
    readme = LayerDocFileSuite(
        'README.rst',
        zope.app.apidoc.utilitymodule)

    browser = LayerDocFileSuite(
        'browser.rst',
        zope.app.apidoc.utilitymodule)

    return unittest.TestSuite((
        readme,
        browser,
        unittest.defaultTestLoader.loadTestsFromName(__name__),
    ))
