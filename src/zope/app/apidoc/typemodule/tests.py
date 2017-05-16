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
"""Tests for the Book Documentation Module

"""
import unittest
import doctest

from zope.component import testing
from zope.app.apidoc.tests import BrowserTestCase

from zope.app.apidoc.testing import APIDocLayer


class TypeModuleTests(BrowserTestCase):
    """Just a couple of tests ensuring that the templates render."""

    layer = APIDocLayer

    def testMenu(self):
        response = self.publish(
            '/++apidoc++/Type/@@menu.html',
            basic='mgr:mgrpw')
        self.assertEqual(response.getStatus(), 200)
        body = response.getBody()
        self.assert_(body.find('IBrowserSkinType') > 0)
        self.checkForBrokenLinks(body, '/++apidoc++/Type/@@menu.html',
                                 basic='mgr:mgrpw')


def test_suite():
    return unittest.TestSuite((
        doctest.DocTestSuite('zope.app.apidoc.typemodule.type',
                             setUp=testing.setUp,
                             tearDown=testing.tearDown),
        unittest.defaultTestLoader.loadTestsFromName(__name__),
    ))

if __name__ == '__main__':
    unittest.main(default='test_suite')
