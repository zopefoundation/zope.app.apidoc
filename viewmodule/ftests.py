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
"""Functional Tests for Presentation Documentation Module.

$Id$
"""
import unittest
from zope.app.tests.functional import BrowserTestCase

class ViewModuleTests(BrowserTestCase):
    """Just a couple of tests ensuring that the templates render."""

    def testMenu(self):
        response = self.publish('/++apidoc++/Views/menu.html', 
                                basic='mgr:mgrpw')
        self.assertEqual(response.getStatus(), 200)
        body = response.getBody()
        self.assert_(body.find('Show Skins and Layers') > 0)
        self.checkForBrokenLinks(body, '/++apidoc++/Views/menu.html',
                                 basic='mgr:mgrpw')


    def testSkinsLayersView(self):
        response = self.publish('/++apidoc++/Views/skin_layer.html',
                                basic='mgr:mgrpw')
        self.assertEqual(response.getStatus(), 200)
        body = response.getBody()
        self.assert_(body.find('Skin-Layer Tree') > 0)

    def testViewsDetails(self):
        response = self.publish(
            '/++apidoc++/Views/index.html',
            form={'iface': 'zope.app.apidoc.interfaces.IDocumentationModule',
                  'type': 'zope.publisher.interfaces.browser.IBrowserRequest',
                  'all': 'all'},
            basic='mgr:mgrpw')
        self.assertEqual(response.getStatus(), 200)
        body = response.getBody()
        self.assert_(body.find(
            'IBrowserRequest\n        <span>views for</span>\n'
            '    IDocumentationModule') > 0)
        self.checkForBrokenLinks(
            body, '/++apidoc++/Views/index.html',
            basic='mgr:mgrpw')
        

def test_suite():
    return unittest.TestSuite((
        unittest.makeSuite(ViewModuleTests),
        ))

if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')
