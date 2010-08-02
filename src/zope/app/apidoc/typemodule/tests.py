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

$Id$
"""
import unittest
import doctest

from zope.app.testing.functional import BrowserTestCase
from zope.app.testing import placelesssetup
from zope.app.apidoc.testing import APIDocLayer


class TypeModuleTests(BrowserTestCase):
    """Just a couple of tests ensuring that the templates render."""

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
    TypeModuleTests.layer = APIDocLayer
    return unittest.TestSuite((
        doctest.DocTestSuite('zope.app.apidoc.typemodule.type',
                             setUp=placelesssetup.setUp,
                             tearDown=placelesssetup.tearDown),
        unittest.makeSuite(TypeModuleTests),
        ))

if __name__ == '__main__':
    unittest.main(default='test_suite')
