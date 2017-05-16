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
import os
import unittest
import doctest

from zope.configuration import xmlconfig
import zope.app.appsetup.appsetup
from zope.component import testing


def setUp(test):
    testing.setUp()

    meta = '''
    <configure
        xmlns:meta="http://namespaces.zope.org/meta"
        i18n_domain="zope">
      <meta:provides feature="devmode" />
      <include package="zope.app.apidoc" file="ftesting.zcml" />
    </configure>
    '''
    context = xmlconfig.string(meta)

    # ctx = xmlconfig.file('meta.zcml', zope.security)
    # ctx = xmlconfig.file('meta.zcml', ztapi, context=ctx)
    # ctx = xmlconfig.file('meta.zcml', zope.browserresource, context=ctx)
    # ctx = xmlconfig.file('meta.zcml', zope.browserpage, context=ctx)
    # ctx = xmlconfig.file('configure.zcml', zope.location, context=ctx)
    # ctx = xmlconfig.file('configure.zcml', zope.traversing, context=ctx)
    # ctx = xmlconfig.file('configure.zcml', zope.security, context=ctx)
    # xmlconfig.file('configure.zcml', zope.app.tree, context=ctx)


    # meta = os.path.join(os.path.dirname(zope.app.zcmlfiles.__file__), 'meta.zcml')
    # context = xmlconfig.file(meta, zope.app.zcmlfiles)
    # context.provideFeature('devmode')
    # meta = os.path.join(os.path.dirname(zope.app.apidoc.__file__), 'meta.zcml')
    # context = xmlconfig.file(meta, zope.app.apidoc, context)

    # Fix up path for tests.
    global old_context
    old_context = zope.app.appsetup.appsetup.__config_context
    zope.app.appsetup.appsetup.__config_context = context

def tearDown(test):
    testing.tearDown()
    global old_context
    zope.app.appsetup.appsetup.__config_context = old_context


def test_suite():
    return unittest.TestSuite((
        doctest.DocFileSuite('README.rst',
                             setUp=setUp, tearDown=tearDown,
                             optionflags=doctest.NORMALIZE_WHITESPACE),
        doctest.DocFileSuite('directives.rst',
                             setUp=testing.setUp,
                             tearDown=testing.tearDown),
    ))

if __name__ == '__main__':
    unittest.main(default="test_suite")
