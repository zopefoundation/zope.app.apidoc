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
"""Tests for the Service Documentation Module

$Id$
"""
import unittest
from zope.testing.doctestunit import DocTestSuite
from zope.app.tests import placelesssetup, ztapi

from zope.app.tree.interfaces import IUniqueId
from zope.app.tree.adapters import LocationUniqueId 

from zope.app.traversing.interfaces import IPhysicallyLocatable
from zope.app.location.traversing import LocationPhysicallyLocatable

def setUp(test):
    placelesssetup.setUp()
    ztapi.provideAdapter(None, IUniqueId, LocationUniqueId)
    ztapi.provideAdapter(None, IPhysicallyLocatable,
                         LocationPhysicallyLocatable)

def test_suite():
    return unittest.TestSuite((
        DocTestSuite('zope.app.apidoc.servicemodule'),
        DocTestSuite('zope.app.apidoc.servicemodule.browser',
                     setUp=setUp, tearDown=placelesssetup.tearDown),
        ))

if __name__ == '__main__':
    unittest.main()
