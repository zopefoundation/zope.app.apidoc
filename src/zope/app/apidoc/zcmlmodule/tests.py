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
import unittest

import zope.app.apidoc.zcmlmodule
from zope.app.apidoc.testing import APIDocLayer
from zope.app.apidoc.tests import BrowserTestCase
from zope.app.apidoc.tests import LayerDocFileSuite


class ZCMLModuleTests(BrowserTestCase):
    """Just a couple of tests ensuring that the templates render."""
    layer = APIDocLayer

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
    return unittest.TestSuite((
        LayerDocFileSuite(
            'README.rst',
            zope.app.apidoc.zcmlmodule),
        LayerDocFileSuite(
            'browser.rst',
            zope.app.apidoc.zcmlmodule),
        unittest.defaultTestLoader.loadTestsFromName(__name__),
    ))
