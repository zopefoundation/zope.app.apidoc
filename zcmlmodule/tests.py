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
"""Tests for the ZCML Documentation Module

$Id$
"""
import os
import unittest
from zope.testing.doctestunit import DocTestSuite
from zope.app.tests import placelesssetup, ztapi
from zope.app.apidoc.tests import Root

import zope.app.appsetup.appsetup
from zope.app.location.traversing import LocationPhysicallyLocatable
from zope.app.traversing.interfaces import IPhysicallyLocatable
from zope.app.tree.interfaces import IUniqueId
from zope.app.tree.adapters import LocationUniqueId 

from zope.app.apidoc.zcmlmodule import Namespace, Directive
from zope.app.apidoc.zcmlmodule import ZCMLModule
from zope.app.apidoc.tests import Root


def setUp(test):
    placelesssetup.setUp()

    ztapi.provideAdapter(None, IUniqueId, LocationUniqueId)
    ztapi.provideAdapter(None, IPhysicallyLocatable,
                         LocationPhysicallyLocatable)

    # Fix up path for tests.
    global old_source_file
    old_source_file = zope.app.appsetup.appsetup.__config_source
    zope.app.appsetup.appsetup.__config_source = os.path.join(
        os.path.dirname(zope.app.__file__), 'meta.zcml')

def tearDown(test):
    placelesssetup.tearDown()
    zope.app.appsetup.appsetup.__config_source = old_source_file    

def getDirective():
    module = ZCMLModule()
    module.__parent__ = Root()
    module.__name__ = 'ZCML'

    def foo(): pass

    ns = Namespace(module, 'http://namespaces.zope.org/browser')
    return Directive(ns, 'page', None, foo, None, ())
    

def test_suite():
    return unittest.TestSuite((
        DocTestSuite('zope.app.apidoc.zcmlmodule',
                     setUp=setUp, tearDown=tearDown),
        DocTestSuite('zope.app.apidoc.zcmlmodule.browser',
                     setUp=setUp, tearDown=tearDown),
        ))

if __name__ == '__main__':
    unittest.main()
