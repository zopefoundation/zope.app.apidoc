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
"""Tests for the Interface Documentation Module

$Id$
"""
from pprint import PrettyPrinter
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
    service = zapi.getGlobalService('Utilities')
    service.provideUtility(IDocumentationModule, InterfaceModule(),
                           'Interface')
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


def _convertToSortedSequence(obj):
    """Convert data structures containing dictionaries to data structures
    using sequences only.

    Examples::

      >>> _convertToSortedSequence(())
      ()
      >>> _convertToSortedSequence({})
      []
      >>> _convertToSortedSequence({'foo': 1})
      [('foo', 1)]
      >>> _convertToSortedSequence({'foo': 1, 'bar': 2})
      [('bar', 2), ('foo', 1)]
      >>> _convertToSortedSequence({'foo': {1: 'a'}, 'bar': 2})
      [('bar', 2), ('foo', [(1, 'a')])]
    """

    # Handle incoming sequences
    if isinstance(obj, (tuple, list)):
        objtype = type(obj)
        result = []
        for value in obj:
            result.append(_convertToSortedSequence(value))
        return objtype(result)

    # Handle Dictionaries
    if isinstance(obj, dict):
        result = []
        for key, value in obj.items():
            result.append((key, _convertToSortedSequence(value)))
        result.sort()
        return result

    return obj


def pprint(info):
    """Print a datastructure in a nice format."""
    info = _convertToSortedSequence(info)
    return PrettyPrinter(width=69).pprint(info)


    
def test_suite():
    return unittest.TestSuite((
        #DocTestSuite('zope.app.apidoc',
        #             setUp=setUp, tearDown=tearDown),
        #DocTestSuite('zope.app.apidoc.browser.apidoc',
        #             setUp=setUp, tearDown=tearDown),
        #DocTestSuite('zope.app.apidoc.utilities'),
        DocTestSuite('zope.app.apidoc.tests'),
        ))

if __name__ == '__main__':
    unittest.main()
