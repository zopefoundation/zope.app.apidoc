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

$Id$
"""
import unittest
from zope.component.interfaces import IFactory
from zope.component.factory import Factory
from zope.interface import implements, Interface, Attribute
from zope.interface.interfaces import IInterface
from zope.publisher.browser import TestRequest
from zope.schema import TextLine, Text
from zope.testing.doctestunit import DocTestSuite
from zope.app import zapi
from zope.app.component.interface import provideInterface
from zope.app.location import LocationProxy
from zope.app.tests import placelesssetup, ztapi
from zope.app.traversing.interfaces import IContainmentRoot

from zope.app.tree.interfaces import IUniqueId
from zope.app.tree.adapters import LocationUniqueId 

from zope.app.traversing.interfaces import IPhysicallyLocatable
from zope.app.location import LocationProxy
from zope.app.location.traversing import LocationPhysicallyLocatable

from zope.app.apidoc.classmodule import classRegistry
from zope.app.apidoc.ifacemodule import IInterfaceModule, InterfaceModule
from zope.app.apidoc.ifacemodule.menu import IModule
from zope.app.apidoc.ifacemodule.browser import InterfaceDetails
from zope.app.apidoc.interfaces import IDocumentationModule


class Root:
    implements(IContainmentRoot)

    __parent__ = None
    __name__ = ''

def rootLocation(obj, name):
    return LocationProxy(obj, Root(), name)

class IFoo(Interface):
    """This is the Foo interface

    More description here...
    """
    foo = Attribute('This is foo.')
    bar = Attribute('This is bar.')

    title = TextLine(description=u'Title', required=True, default=u'Foo')
    description = Text(description=u'Desc', required=False, default=u'Foo.')

    def blah():
        """This is blah."""
    
    def get(key, default=None):
        """This is get."""

class IBar(Interface):
    pass

class Foo:
    implements(IFoo)


def getInterfaceDetails():
    ifacemodule = InterfaceModule()
    ifacemodule.__parent__ = Root()
    ifacemodule.__name__ = 'Interfaces'
    iface = LocationProxy(IFoo, ifacemodule, 'IFoo')
    view = InterfaceDetails()
    view.context = iface
    view.request = TestRequest()
    return view
    

def setUp():
    placelesssetup.setUp()
    provideInterface(None, IDocumentationModule)
    provideInterface('IInterfaceModule', IInterfaceModule)
    ztapi.provideAdapter(IInterface, IUniqueId, LocationUniqueId)
    ztapi.provideAdapter(None, IPhysicallyLocatable,
                         LocationPhysicallyLocatable)

    # Make IFoo adapter interesting.

    ztapi.provideAdapter(IBar, IFoo, object)
    classRegistry[Foo.__module__ + '.' + Foo.__name__] = Foo
    ztapi.provideUtility(IFactory, Factory(Foo, title='Foo Factory'),
                         'FooFactory')
    ztapi.provideUtility(IFoo, Foo(), 'The Foo')
    sm = zapi.getService(None, 'Services')
    sm.defineService('Foo', IFoo)
    sm.provideService('Foo', Foo())

def tearDown():
    placelesssetup.tearDown()
    
def test_suite():
    return unittest.TestSuite((
        DocTestSuite('zope.app.apidoc.ifacemodule',
                     setUp=setUp, tearDown=tearDown),
        DocTestSuite('zope.app.apidoc.ifacemodule.menu',
                     setUp=setUp, tearDown=tearDown),
        DocTestSuite('zope.app.apidoc.ifacemodule.browser',
                     setUp=setUp, tearDown=tearDown),
        ))

if __name__ == '__main__':
    unittest.main()
