##############################################################################
#
# Copyright (c) 2004 Zope Foundation and Contributors.
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

"""
from __future__ import absolute_import
import os
import unittest
import doctest
import re

from zope import component as ztapi
from zope import interface
from zope.component.interfaces import IFactory
from zope.configuration import xmlconfig
from zope.interface import implementer
from zope.testing import renormalizing

from zope.app.component.testing import PlacefulSetup
import zope.app
import zope.app.appsetup.appsetup
from zope.app.renderer.rest import ReStructuredTextSourceFactory
from zope.app.renderer.rest import IReStructuredTextSource
from zope.app.renderer.rest import ReStructuredTextToHTMLRenderer
from zope.app.apidoc.tests import BrowserTestCase


from zope.app.apidoc.apidoc import apidocNamespace
from zope.traversing.interfaces import ITraversable
from zope.app.apidoc.interfaces import IDocumentationModule
from zope.app.apidoc.apidoc import APIDocumentation
from zope.app.apidoc.codemodule.interfaces import IAPIDocRootModule
from zope.app.apidoc.codemodule.codemodule import CodeModule
from zope.app.apidoc.testing import APIDocLayer
from zope.app.apidoc.zcmlmodule import ZCMLModule

# Just for loading purposes
import zope.app.apidoc.codemodule.browser.module
import zope.app.apidoc.codemodule.browser.class_
import zope.app.apidoc.codemodule.browser.function
import zope.app.apidoc.codemodule.browser.text
import zope.app.apidoc.codemodule.browser.zcml


def foo(cls, bar=1, *args):
    """This is the foo function."""
foo.deprecated = True

# meta = '''
# <configure
#     xmlns:meta="http://namespaces.zope.org/meta"
#     i18n_domain="zope">
#   <meta:provides feature="devmode" />
#   <include package="zope.app.zcmlfiles" file="meta.zcml" />
#   <include package="zope.app.apidoc" file="meta.zcml" />
#   <include package="zope.app.zcmlfiles" file="menus.zcml" />
# </configure>
# '''

def _setUp_AppSetup():
    config_file = os.path.join(
        os.path.dirname(zope.app.apidoc.__file__), 'configure.zcml')

    # # Fix up path for tests.
    global old_context
    old_context = zope.app.appsetup.appsetup.getConfigContext()
    zope.app.appsetup.appsetup.__config_context = xmlconfig.file(
        config_file, zope.app.apidoc, execute=False)

def _tearDown_AppSetup():
    zope.app.appsetup.appsetup.__config_context = old_context


def setUp(test):
    test.globs['rootFolder'] = PlacefulSetup().setUp(True, True)
    # from zope.interface import alsoProvides
    # from zope.annotation.interfaces import IAnnotatable
    # alsoProvides(test.globs['rootFolder'], IAnnotatable)
    # alsoProvides(test.globs['rootFolder'].__parent__, IAnnotatable)

    @implementer(IAPIDocRootModule)
    class RootModule(str):
        pass

    # Register zope package to apidoc
    ztapi.provideUtility(RootModule('zope'), IAPIDocRootModule, "zope")

    # Set up apidoc module
    test.globs['apidoc'] = APIDocumentation(test.globs['rootFolder'],
                                            '++apidoc++')


    # Register Renderer Components
    # ztapi.provideUtility(IFactory, ReStructuredTextSourceFactory,
    #                      'zope.source.rest')
    # ztapi.browserView(IReStructuredTextSource, '',
    #                   ReStructuredTextToHTMLRenderer)
    # # Cheat and register the ReST factory for STX as well.
    # ztapi.provideUtility(IFactory, ReStructuredTextSourceFactory,
    #                      'zope.source.stx')
    import zope.app.renderer
    context = xmlconfig.file('ftesting.zcml', zope.app.apidoc)

    from zope.dublincore.interfaces import IWriteZopeDublinCore
    IWriteZopeDublinCore(test.globs['rootFolder'].__parent__)

    # Register documentation modules. Override what we got from
    # ftesting-base (non-devmode)
    # ztapi.provideUtility(CodeModule(), IDocumentationModule,"Code")
    # ztapi.provideUtility(ZCMLModule(), IDocumentationModule, "ZCML")

    # Register ++apidoc++ namespace
    # from zope.app.apidoc.apidoc import apidocNamespace
    # from zope.traversing.interfaces import ITraversable
    # ztapi.provideAdapter(apidocNamespace, (interface.Interface,), ITraversable, name="apidoc")
    # ztapi.provideView(None, None, ITraversable, "apidoc", apidocNamespace)

    # Register ++apidoc++ namespace
    # ztapi.provideView(None, None, ITraversable, "view", view)
    # from zope.traversing.namespace import view
    # from zope.traversing.interfaces import ITraversable
    # ztapi.provideAdapter(None, ITraversable, view, name="view")

    # context = xmlconfig.string(meta)

    # Fix up path for tests.
    global old_context
    old_context = zope.app.appsetup.appsetup.__config_context
    zope.app.appsetup.appsetup.__config_context = context

    # Fix up path for tests.
    global old_source_file
    old_source_file = zope.app.appsetup.appsetup.__config_source
    zope.app.appsetup.appsetup.__config_source = os.path.join(
        os.path.dirname(zope.app.apidoc.__file__), 'meta.zcml')

    # Register the index.html view for codemodule.class_.Class
    # from zope.publisher.browser import BrowserView
    # from zope.app.apidoc.codemodule.class_ import Class
    # from zope.app.apidoc.codemodule.browser.class_ import ClassDetails
    # class Details(ClassDetails, BrowserView):
    #     pass
    # ztapi.browserView(Class, 'index.html', Details)


def tearDown(test):
    PlacefulSetup().tearDown()
    global old_context, old_source_file
    zope.app.appsetup.appsetup.__config_context = old_context
    zope.app.appsetup.appsetup.__config_source = old_source_file


class CodeModuleTests(BrowserTestCase):
    """Just a couple of tests ensuring that the templates render."""

    def testMenu(self):
        response = self.publish('/++apidoc++/Code/menu.html',
                                basic='mgr:mgrpw')
        self.assertEqual(response.getStatus(), 200)
        body = response.getBody()
        self.assert_(body.find('Zope Source') > 0)
        self.checkForBrokenLinks(body, '/++apidoc++/Code/menu.html',
                                 basic='mgr:mgrpw')

    def testMenuCodeFinder(self):
        response = self.publish('/++apidoc++/Code/menu.html',
                                basic='mgr:mgrpw',
                                form={'path': 'Code', 'SUBMIT': 'Find'})
        self.assertEqual(response.getStatus(), 200)
        body = response.getBody()
        self.assert_(
            body.find('zope.app.apidoc.codemodule.codemodule.CodeModule') > 0)
        self.checkForBrokenLinks(body, '/++apidoc++/Code/menu.html',
                                 basic='mgr:mgrpw')

    def testModuleDetailsView(self):
        response = self.publish('/++apidoc++/Code/zope/app/apidoc/apidoc',
                                basic='mgr:mgrpw')
        self.assertEqual(response.getStatus(), 200)
        body = response.getBody()
        self.assert_(body.find('Zope 3 API Documentation') > 0)
        self.checkForBrokenLinks(
            body, '/++apidoc++/Code/zope/app/apidoc/apidoc', basic='mgr:mgrpw')

    def testClassDetailsView(self):
        response = self.publish(
            '/++apidoc++/Code/zope/app/apidoc/apidoc/APIDocumentation',
            basic='mgr:mgrpw')
        self.assertEqual(response.getStatus(), 200)
        body = response.getBody()
        self.assert_(body.find('Represent the complete API Documentation.') > 0)
        self.checkForBrokenLinks(
            body, '/++apidoc++/Code/zope/app/apidoc/apidoc/APIDocumentation',
            basic='mgr:mgrpw')

    def testFunctionDetailsView(self):
        response = self.publish(
            '/++apidoc++/Code/zope/app/apidoc/apidoc/handleNamespace',
            basic='mgr:mgrpw')
        self.assertEqual(response.getStatus(), 200)
        body = response.getBody()
        self.assert_(body.find('handleNamespace(ob, name)') > 0)
        self.checkForBrokenLinks(
             body,
            '/++apidoc++/Code/zope/app/apidoc/apidoc/handleNamespace',
             basic='mgr:mgrpw')

    def testTextFileDetailsView(self):
        response = self.publish(
            '/++apidoc++/Code/zope/app/apidoc/README.rst/index.html',
            basic='mgr:mgrpw')
        self.assertEqual(response.getStatus(), 200)
        body = response.getBody()
        self.checkForBrokenLinks(
            body, '/++apidoc++/Code/zope/app/apidoc/README.rst/index.html',
            basic='mgr:mgrpw')

    def testZCMLFileDetailsView(self):
        response = self.publish(
            '/++apidoc++/Code/zope/app/apidoc/configure.zcml/index.html',
            basic='mgr:mgrpw')
        self.assertEqual(response.getStatus(), 200)
        body = response.getBody()
        self.checkForBrokenLinks(
            body, '/++apidoc++/Code/zope/app/apidoc/configure.zcml/index.html',
            basic='mgr:mgrpw')


def test_suite():
    checker = renormalizing.RENormalizing([
        (re.compile(r" with base 10: 'text'"), r': text'),
    ])
    CodeModuleTests.layer = APIDocLayer
    introspector = doctest.DocFileSuite(
        "introspector.rst",
        optionflags=doctest.ELLIPSIS | doctest.NORMALIZE_WHITESPACE)
    introspector.layer = APIDocLayer
    return unittest.TestSuite((
        doctest.DocFileSuite(
            'README.rst',
            setUp=setUp, tearDown=tearDown,checker=checker,
            optionflags=doctest.NORMALIZE_WHITESPACE|doctest.ELLIPSIS),
        doctest.DocTestSuite(
            'zope.app.apidoc.codemodule.browser.menu',
            setUp=setUp, tearDown=tearDown,
            optionflags=doctest.NORMALIZE_WHITESPACE),
        unittest.makeSuite(CodeModuleTests),
        introspector,
    ))

if __name__ == '__main__':
    unittest.main()
