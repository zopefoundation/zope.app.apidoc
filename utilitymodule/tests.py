##############################################################################
#
# Copyright (c) 2004 Zope Corporation and Contributors.
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

$Id$
"""
import unittest

from zope.interface import implements
from zope.publisher.browser import TestRequest
from zope.testing.doctestunit import DocTestSuite

from zope.app import zapi
from zope.app.tests import placelesssetup, ztapi

from zope.app.apidoc.interfaces import IDocumentationModule
from zope.app.apidoc.tests import Root
from zope.app.apidoc.ifacemodule import InterfaceModule
from zope.app.apidoc.classmodule import ClassModule
from zope.app.apidoc.utilitymodule import UtilityModule, Utility
from browser import UtilityDetails

from zope.app.tree.interfaces import IUniqueId
from zope.app.tree.adapters import LocationUniqueId 

from zope.app.traversing.interfaces import IPhysicallyLocatable
from zope.app.location.traversing import LocationPhysicallyLocatable


def setUp(test):
    placelesssetup.setUp()
    service = zapi.getGlobalService('Utilities')
    service.provideUtility(IDocumentationModule, InterfaceModule(), '')
    service.provideUtility(IDocumentationModule, ClassModule(), 'Classes')

    ztapi.provideAdapter(None, IUniqueId, LocationUniqueId)
    ztapi.provideAdapter(None, IPhysicallyLocatable,
                         LocationPhysicallyLocatable)


def makeRegistration(name, interface, component):
    return type('RegistrationStub', (),
                {'name': name, 'provided': interface,
                 'component': component, 'doc': ''})()

def getDetailsView():
    utils = UtilityModule()
    utils.__parent__ = Root
    utils.__name__ = 'Utility'
    util = Utility(
        utils,
        makeRegistration('Classes', IDocumentationModule, ClassModule()))
    details = UtilityDetails()
    details.context = util
    details.request = TestRequest()
    return details

def test_suite():
    return unittest.TestSuite((
        DocTestSuite('zope.app.apidoc.utilitymodule',
                     setUp=setUp, tearDown=placelesssetup.tearDown),
        DocTestSuite('zope.app.apidoc.utilitymodule.browser',
                     setUp=setUp, tearDown=placelesssetup.tearDown),
        ))

if __name__ == '__main__':
    unittest.main()
