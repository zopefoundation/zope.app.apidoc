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
"""Tests for the Code Documentation Module

$Id$
"""
import unittest
from zope.component.interfaces import IFactory
from zope.configuration import xmlconfig
from zope.interface import Interface, directlyProvides, implements
from zope.publisher.browser import TestRequest
from zope.testing.doctestunit import DocTestSuite

from zope.app import zapi
from zope.app.location.traversing import LocationPhysicallyLocatable
from zope.app.renderer.rest import ReStructuredTextSourceFactory
from zope.app.renderer.rest import IReStructuredTextSource
from zope.app.renderer.rest import ReStructuredTextToHTMLRenderer
from zope.app.renderer.stx import StructuredTextSourceFactory
from zope.app.renderer.stx import IStructuredTextSource
from zope.app.renderer.stx import StructuredTextToHTMLRenderer
from zope.app.testing import placelesssetup, ztapi
from zope.app.traversing.browser import AbsoluteURL, SiteAbsoluteURL
from zope.app.traversing.interfaces import ITraversable, ITraverser
from zope.app.traversing.interfaces import IPhysicallyLocatable
from zope.app.traversing.interfaces import IContainmentRoot
from zope.app.traversing.adapters import DefaultTraversable
from zope.app.traversing.adapters import RootPhysicallyLocatable
from zope.app.traversing.adapters import Traverser

from zope.app.apidoc.codemodule import CodeModule, IAPIDocRootModule
from zope.app.apidoc.codemodule.browser.class_ import ClassDetails
from zope.app.apidoc.codemodule.browser.function import FunctionDetails
from zope.app.apidoc.codemodule.browser.module import ModuleDetails
from zope.app.apidoc.interfaces import IDocumentationModule


def setUp(test):
    placelesssetup.setUp()

    class RootModule(str):
        implements(IAPIDocRootModule)
    ztapi.provideUtility(IAPIDocRootModule, RootModule('zope'), "zope")

    module = CodeModule()
    module.__name__ = ''
    directlyProvides(module, IContainmentRoot)
    ztapi.provideUtility(IDocumentationModule, module, "Code")

    ztapi.provideAdapter(
        None, ITraverser, Traverser)
    ztapi.provideAdapter(
        None, ITraversable, DefaultTraversable)
    ztapi.provideAdapter(
        None, IPhysicallyLocatable, LocationPhysicallyLocatable)
    ztapi.provideAdapter(
        IContainmentRoot, IPhysicallyLocatable, RootPhysicallyLocatable)

    ztapi.browserView(Interface, "absolute_url", AbsoluteURL)
    ztapi.browserView(IContainmentRoot, "absolute_url", SiteAbsoluteURL)

    # Register Renderer Components
    ztapi.provideUtility(IFactory, StructuredTextSourceFactory,
                         'zope.source.stx')    
    ztapi.provideUtility(IFactory, ReStructuredTextSourceFactory,
                         'zope.source.rest')    
    ztapi.browserView(IStructuredTextSource, '', 
                      StructuredTextToHTMLRenderer)
    ztapi.browserView(IReStructuredTextSource, '', 
                      ReStructuredTextToHTMLRenderer)


def foo(cls, bar=1, *args):
    """This is the foo function."""
foo.deprecated = True


def getFunctionDetailsView():
    cm = zapi.getUtility(IDocumentationModule, 'Code')
    view = FunctionDetails()
    view.context = zapi.traverse(cm, 'zope/app/apidoc/codemodule/tests/foo')
    view.request = TestRequest()
    return view


def getClassDetailsView():
    cm = zapi.getUtility(IDocumentationModule, 'Code')
    view = CodeDetails()
    view.context = zapi.traverse(cm, 'zope/app/apidoc/codemodule/CodeModule')
    view.request = TestRequest()
    return view


def getModuleDetailsView():
    cm = zapi.getUtility(IDocumentationModule, 'Code')
    view = ModuleDetails()
    view.context = zapi.traverse(cm, 'zope/app/apidoc/codemodule')
    view.request = TestRequest()
    return view


class DirectivesTest(placelesssetup.PlacelessSetup, unittest.TestCase):

    template = """
        <configure
            xmlns='http://namespaces.zope.org/apidoc'>
          %s
        </configure>"""
    
    def setUp(self):
        super(DirectivesTest, self).setUp()
        import zope.app.apidoc.codemodule
        self.context = xmlconfig.file('meta.zcml', zope.app.apidoc.codemodule)

    def testRootModule(self):
        self.assertEqual(len(list(zapi.getUtilitiesFor(IAPIDocRootModule))), 0)
        xmlconfig.string(
            self.template %'<rootModule module="zope" />', self.context)

        self.assertEqual(zapi.getUtilitiesFor(IAPIDocRootModule).next()[0],
                         'zope')


def test_suite():
    return unittest.TestSuite((
        # XXX: Redo browser tests
        #DocTestSuite('zope.app.apidoc.codemodule.browser',
        #             setUp=setUp, tearDown=placelesssetup.tearDown),
        DocTestSuite('zope.app.apidoc.codemodule',
                     setUp=setUp, tearDown=placelesssetup.tearDown),
        unittest.makeSuite(DirectivesTest),
        ))

if __name__ == '__main__':
    unittest.main()
