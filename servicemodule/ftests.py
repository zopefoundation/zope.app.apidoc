##############################################################################
#
# Copyright (c) 2003, 2004 Zope Corporation and Contributors.
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
"""Functional Tests for Service Documentation Module.

$Id$
"""
import unittest
from zope.app.tests.functional import BrowserTestCase

class ServiceModuleTests(BrowserTestCase):
    """Just a couple of tests ensuring that the templates render."""

    def testMenu(self):
        response = self.publish(
            '/++apidoc++/Service/menu.html', 
            basic='mgr:mgrpw')
        self.assertEqual(response.getStatus(), 200)
        body = response.getBody()
        self.assert_(body.find('Services') > 0)
        self.checkForBrokenLinks(body, '/++apidoc++/Service/menu.html',
                                 basic='mgr:mgrpw')

    def testServiceDetailsView(self):
        response = self.publish(
            '/++apidoc++/Service/Services/index.html',
            basic='mgr:mgrpw')
        self.assertEqual(response.getStatus(), 200)
        body = response.getBody()
        self.assert_(body.find('Services Service') > 0)
        self.checkForBrokenLinks(body,
                                 '/++apidoc++/Service/Services/index.html',
                                 basic='mgr:mgrpw')


def test_suite():
    return unittest.TestSuite((
        unittest.makeSuite(ServiceModuleTests),
        ))

if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')
