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

import doctest
import unittest

from zope.component import testing

from zope.app.apidoc.testing import APIDocLayer
from zope.app.apidoc.tests import BrowserTestCase
from zope.app.apidoc.tests import standard_option_flags


class TypeModuleTests(BrowserTestCase):
    """Just a couple of tests ensuring that the templates render."""

    layer = APIDocLayer

    def testMenu(self):
        response = self.publish(
            '/++apidoc++/Type/@@menu.html',
            basic='mgr:mgrpw')
        self.assertEqual(response.getStatus(), 200)
        body = response.getBody()
        self.assertIn('IBrowserSkinType', body)
        self.checkForBrokenLinks(body, '/++apidoc++/Type/@@menu.html',
                                 basic='mgr:mgrpw')


def test_suite():
    return unittest.TestSuite((
        doctest.DocTestSuite(
            'zope.app.apidoc.typemodule.type',
            setUp=testing.setUp,
            tearDown=testing.tearDown,
            optionflags=standard_option_flags),
        unittest.defaultTestLoader.loadTestsFromName(__name__),
    ))
