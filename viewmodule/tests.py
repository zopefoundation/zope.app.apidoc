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
from zope.interface import Interface
from zope.publisher.interfaces.browser import IBrowserRequest
from zope.testing.doctestunit import DocTestSuite
from zope.app import zapi
from zope.app.tests import placelesssetup, ztapi
from zope.app.component.interface import provideInterface

from zope.app.apidoc.viewmodule import ISkinRegistration
from zope.app.apidoc.viewmodule import ISkinDocumentation, SkinDocumentation
from zope.app.apidoc.viewmodule import ILayerRegistration
from zope.app.apidoc.viewmodule import ILayerDocumentation, LayerDocumentation

class IFoo(Interface):
    pass

class FooView(object):
    pass

def setUp(test):
    placelesssetup.setUp()

    ztapi.provideAdapter(ISkinRegistration, ISkinDocumentation,
                         SkinDocumentation)
    ztapi.provideAdapter(ILayerRegistration, ILayerDocumentation,
                         LayerDocumentation)

    pres = zapi.getGlobalService('Presentation')
    for index in range(1, 6):
        pres.defineLayer('layer'+str(index))
    pres.defineSkin('skinA', ['default'], 'doc skin A')
    pres.defineSkin('skinB', ['layer5', 'layer4', 'default'], 'doc skin B')
    pres.defineSkin('skinC', ['layer4', 'layer2', 'layer1', 'default'],
                    'doc skin C')
    pres.setDefaultSkin('skinA', 'default is A')

    provideInterface('IFoo', IFoo)
    provideInterface('IBrowserRequest', IBrowserRequest)
    ztapi.browserView(IFoo, 'index.html', FooView, layer='default')


def test_suite():
    return unittest.TestSuite((
        DocTestSuite('zope.app.apidoc.viewmodule',
                     setUp=setUp, tearDown=placelesssetup.tearDown),
        DocTestSuite('zope.app.apidoc.viewmodule.browser',
                     setUp=setUp, tearDown=placelesssetup.tearDown),
        ))

if __name__ == '__main__':
    unittest.main()
