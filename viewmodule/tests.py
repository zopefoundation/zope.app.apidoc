##############################################################################
#
# Copyright (c) 2004 Zope Corporation and Contributors.
# All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.0 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
##############################################################################
"""Tests for the Class Documentation Module

$Id: tests.py,v 1.2 2004/03/30 02:01:24 srichter Exp $
"""
import unittest
from zope.interface import Interface
from zope.publisher.interfaces.browser import IBrowserRequest
from zope.testing.doctestunit import DocTestSuite
from zope.app import zapi
from zope.app.tests import placelesssetup, ztapi
from zope.app.component.interface import provideInterface

class IFoo(Interface):
    pass

class FooView:
    pass

def setUp():
    placelesssetup.setUp()
    pres = zapi.getService(None, 'Presentation')
    for index in range(1, 6):
        pres.defineLayer('layer'+str(index))
    pres.defineSkin('skinA', ['default'])
    pres.defineSkin('skinB', ['layer5', 'layer4', 'default'])
    pres.defineSkin('skinC', ['layer4', 'layer2', 'layer1', 'default'])

    provideInterface('IFoo', IFoo)
    provideInterface('IBrowserRequest', IBrowserRequest)
    ztapi.browserView(IFoo, 'index.html', FooView, layer='default')
    

def tearDown():
    placelesssetup.tearDown()


def test_suite():
    return unittest.TestSuite((
        DocTestSuite('zope.app.apidoc.viewmodule',
                     setUp=setUp, tearDown=tearDown),
        DocTestSuite('zope.app.apidoc.viewmodule.browser',
                     setUp=setUp, tearDown=tearDown),
        ))

if __name__ == '__main__':
    unittest.main()
