##############################################################################
#
# Copyright (c) 2003, 2004 Zope Foundation and Contributors.
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
"""Functional Tests for API Documentation.

"""
import doctest
import unittest

from zope.app.apidoc.testing import APIDocLayer
from zope.app.apidoc.testing import APIDocNoDevModeLayer
from zope.app.apidoc.tests import BrowserTestCase
from zope.app.apidoc.tests import standard_option_flags


class APIDocTests(BrowserTestCase):
    """Just a couple of tests ensuring that the templates render."""

    layer = APIDocLayer

    def testMenu(self):
        response = self.publish('/++apidoc++/menu.html',
                                basic='mgr:mgrpw')
        self.assertEqual(response.getStatus(), 200)
        body = response.getBody()
        self.assertTrue(body.find('Click on one of the Documentation') > 0)
        self.checkForBrokenLinks(body, '/++apidoc++/menu.html',
                                 basic='mgr:mgrpw')

    def testIndexView(self):
        response = self.publish('/++apidoc++/index.html',
                                basic='mgr:mgrpw')
        self.assertEqual(response.getStatus(), 200)
        body = response.getBody()
        self.assertTrue(body.find('Zope 3 API Documentation') > 0)
        self.checkForBrokenLinks(body, '/++apidoc++/index.html',
                                 basic='mgr:mgrpw')

    def testContentsView(self):
        response = self.publish('/++apidoc++/contents.html',
                                basic='mgr:mgrpw')
        self.assertEqual(response.getStatus(), 200)
        body = response.getBody()
        self.assertTrue(body.find('<h1>Zope 3 API Documentation</h1>') > 0)
        self.checkForBrokenLinks(body, '/++apidoc++/contents.html',
                                 basic='mgr:mgrpw')

    def testModuleListView(self):
        response = self.publish('/++apidoc++/modulelist.html',
                                basic='mgr:mgrpw')
        self.assertEqual(response.getStatus(), 200)
        body = response.getBody()
        self.assertTrue(body.find(
            '<a href="contents.html" target="main">Zope') > 0)
        self.checkForBrokenLinks(body, '/++apidoc++/modulelist.html',
                                 basic='mgr:mgrpw')


def test_suite():
    apidoc_doctest = doctest.DocFileSuite(
        "README.rst",
        optionflags=standard_option_flags)
    apidoc_doctest.layer = APIDocLayer

    nodevmode = doctest.DocFileSuite(
        "nodevmode.rst",
        optionflags=standard_option_flags)
    nodevmode.layer = APIDocNoDevModeLayer

    return unittest.TestSuite((
        apidoc_doctest,
        nodevmode,
        unittest.defaultTestLoader.loadTestsFromName(__name__),
    ))
