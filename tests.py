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
"""Tests for the Interface Documentation Module

$Id: tests.py,v 1.3 2004/03/28 23:39:20 srichter Exp $
"""
import pprint
import unittest
from zope.app import zapi
from zope.app.traversing.interfaces import IContainmentRoot
from zope.app.location import LocationProxy
from zope.app.tests import placelesssetup
from zope.interface import implements
from zope.app.apidoc.interfaces import IDocumentationModule
from zope.app.apidoc.ifacemodule import InterfaceModule
from zope.app.apidoc.zcmlmodule import ZCMLModule
from zope.testing.doctestunit import DocTestSuite


def setUp():
    placelesssetup.setUp()
    service = zapi.getService(None, 'Utilities')
    service.provideUtility(IDocumentationModule, InterfaceModule(), 'Interface')
    service.provideUtility(IDocumentationModule, ZCMLModule(), 'ZCML')

def tearDown():
    placelesssetup.tearDown()


# Generally useful classes and functions

class Root:
    implements(IContainmentRoot)

    __parent__ = None
    __name__ = ''

def rootLocation(obj, name):
    return LocationProxy(obj, Root(), name)


def pprintDict(info):
    print_ = pprint.PrettyPrinter(width=69).pprint
    info = info.items()
    info.sort()
    return print_(info)


    
def test_suite():
    return unittest.TestSuite((
        DocTestSuite('zope.app.apidoc',
                     setUp=setUp, tearDown=tearDown),
        DocTestSuite('zope.app.apidoc.browser.apidoc',
                     setUp=setUp, tearDown=tearDown),
        DocTestSuite('zope.app.apidoc.utilities'),
        ))

if __name__ == '__main__':
    unittest.main()
