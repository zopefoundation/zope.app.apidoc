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
"""Tests for the ZCML Documentation Module

$Id: tests.py,v 1.3 2004/03/29 15:08:54 srichter Exp $
"""
import unittest
from zope.testing.doctestunit import DocTestSuite
from zope.app.tests import placelesssetup, ztapi
from zope.app.apidoc.tests import Root

from zope.app.tree.interfaces import IUniqueId
from zope.app.tree.adapters import LocationUniqueId 

from zope.app.traversing.interfaces import IPhysicallyLocatable
from zope.app.location import LocationPhysicallyLocatable

from zope.app.apidoc.zcmlmodule import Namespace, Directive
from zope.app.apidoc.zcmlmodule import ZCMLModule
from zope.app.apidoc.tests import Root


def setUp():
    placelesssetup.setUp()

    ztapi.provideAdapter(None, IUniqueId, LocationUniqueId)
    ztapi.provideAdapter(None, IPhysicallyLocatable,
                         LocationPhysicallyLocatable)

def tearDown():
    placelesssetup.tearDown()

def getDirective():
    module = ZCMLModule()
    module.__parent__ = Root()
    module.__name__ = 'ZCML'

    def foo(): pass

    ns = Namespace(module, 'http://namespaces.zope.org/browser')
    return Directive(ns, 'page', None, foo, None, ())
    

def test_suite():
    return unittest.TestSuite((
        DocTestSuite('zope.app.apidoc.zcmlmodule'),
        DocTestSuite('zope.app.apidoc.zcmlmodule.browser',
                     setUp=setUp, tearDown=tearDown),
        ))

if __name__ == '__main__':
    unittest.main()
