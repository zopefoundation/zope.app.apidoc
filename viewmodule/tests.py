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
"""Tests for the Class Documentation Module

$Id$
"""
import unittest

from zope.interface import Interface, directlyProvides
from zope.publisher.interfaces.browser import IBrowserRequest
from zope.publisher.interfaces.browser import ISkin, ILayer, IDefaultSkin
from zope.testing.doctestunit import DocTestSuite

from zope.app import zapi
from zope.app.tests import placelesssetup, ztapi
from zope.app.component.interface import provideInterface

class IFoo(Interface):
    pass

class FooView(object):
    pass

class Layer1(IBrowserRequest): pass
class Layer2(IBrowserRequest): pass
class Layer3(IBrowserRequest): pass

class SkinA(IBrowserRequest): pass
class SkinB(Layer1, Layer2): pass
class SkinC(Layer2, Layer3): pass

def setUp(test):
    placelesssetup.setUp()

    provideInterface(u'zope.app.layers.layer1', Layer1)
    provideInterface(u'layer1', Layer1, ILayer, u'layer 1 doc')
    provideInterface(u'zope.app.layers.layer2', Layer2)
    provideInterface(u'layer2', Layer2, ILayer, u'layer 2 doc')
    provideInterface(u'zope.app.layers.layer3', Layer3)
    provideInterface(u'layer3', Layer3, ILayer, u'layer 3 doc')

    provideInterface(u'zope.app.skins.skinA', SkinA)
    provideInterface(u'skinA', SkinA, ISkin, u'skin 1 doc')
    provideInterface(u'zope.app.skins.skinB', SkinB)
    provideInterface(u'skinB', SkinB, ISkin, u'skin 2 doc')
    provideInterface(u'zope.app.skins.skinC', SkinC)
    provideInterface(u'skinC', SkinC, ISkin, u'skin 3 doc')

    ztapi.provideAdapter((IBrowserRequest,), IDefaultSkin, SkinA, '')

    provideInterface('IFoo', IFoo)
    provideInterface('IBrowserRequest', IBrowserRequest)
    ztapi.browserView(IFoo, 'index.html', FooView, layer=Layer1)


def test_suite():
    return unittest.TestSuite((
        DocTestSuite('zope.app.apidoc.viewmodule',
                     setUp=setUp, tearDown=placelesssetup.tearDown),
        DocTestSuite('zope.app.apidoc.viewmodule.browser',
                     setUp=setUp, tearDown=placelesssetup.tearDown),
        ))

if __name__ == '__main__':
    unittest.main()
