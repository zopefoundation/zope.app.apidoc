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

$Id: tests.py 29269 2005-02-23 22:22:48Z srichter $
"""
import os
import unittest
from zope.component.interfaces import IFactory
from zope.configuration import xmlconfig
from zope.interface import directlyProvides, implements
from zope.testing import doctest, doctestunit

import zope.app
import zope.app.appsetup.appsetup
from zope.app.renderer.rest import ReStructuredTextSourceFactory
from zope.app.renderer.rest import IReStructuredTextSource
from zope.app.renderer.rest import ReStructuredTextToHTMLRenderer
from zope.app.testing import placelesssetup, setup, ztapi
from zope.app.traversing.interfaces import IContainmentRoot

from zope.app.apidoc.interfaces import IDocumentationModule
from zope.app.apidoc.codemodule.interfaces import IAPIDocRootModule
from zope.app.apidoc.codemodule.codemodule import CodeModule
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

meta = '''
<configure i18n_domain="zope">
  <include package="zope.app" file="meta.zcml" />
  <include package="zope.app.apidoc" file="meta.zcml" />
  <include package="zope.app" file="menus.zcml" />
</configure>
'''

def setUp(test):
    placelesssetup.setUp()
    setup.setUpTraversal()

    class RootModule(str):
        implements(IAPIDocRootModule)
    ztapi.provideUtility(IAPIDocRootModule, RootModule('zope'), "zope")

    module = CodeModule()
    module.__name__ = ''
    directlyProvides(module, IContainmentRoot)
    ztapi.provideUtility(IDocumentationModule, module, "Code")

    module = ZCMLModule()
    module.__name__ = ''
    directlyProvides(module, IContainmentRoot)
    ztapi.provideUtility(IDocumentationModule, module, "ZCML")

    # Register Renderer Components
    ztapi.provideUtility(IFactory, ReStructuredTextSourceFactory,
                         'zope.source.rest')    
    ztapi.browserView(IReStructuredTextSource, '', 
                      ReStructuredTextToHTMLRenderer)
    # Cheat and register the ReST factory for STX as well.
    ztapi.provideUtility(IFactory, ReStructuredTextSourceFactory,
                         'zope.source.stx')

    context = xmlconfig.string(meta)

    # Fix up path for tests.
    global old_context
    old_context = zope.app.appsetup.appsetup.__config_context
    zope.app.appsetup.appsetup.__config_context = context

    # Fix up path for tests.
    global old_source_file
    old_source_file = zope.app.appsetup.appsetup.__config_source
    zope.app.appsetup.appsetup.__config_source = os.path.join(
        os.path.dirname(zope.app.__file__), 'meta.zcml')


def tearDown(test):
    placelesssetup.tearDown()
    global old_context, old_source_file
    zope.app.appsetup.appsetup.__config_context = old_context    
    zope.app.appsetup.appsetup.__config_source = old_source_file    


def test_suite():
    return unittest.TestSuite((
        doctest.DocFileSuite('README.txt',
                             setUp=setUp, tearDown=tearDown,
                             globs={'pprint': doctestunit.pprint},
                             optionflags=doctest.NORMALIZE_WHITESPACE),
        ))

if __name__ == '__main__':
    unittest.main(default="test_suite")
