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
import unittest
from BTrees import OOBTree

from zope.traversing.api import traverse

from zope.app.apidoc.testing import APIDocLayer
from zope.app.apidoc.tests import BrowserTestCase
from zope.app.apidoc.tests import LayerDocFileSuite
from zope.app.apidoc.tests import LayerDocTestSuite

import zope.app.apidoc.codemodule


def foo(cls, bar=1, *args): # used in README.rst
    """This is the foo function."""
foo.deprecated = True


class CodeModuleTests(BrowserTestCase):
    """Just a couple of tests ensuring that the templates render."""
    layer = APIDocLayer

    def testMenu(self):
        response = self.publish('/++apidoc++/Code/menu.html',
                                basic='mgr:mgrpw')
        self.assertEqual(response.getStatus(), 200)
        body = response.getBody()
        self.assertIn('Zope Source', body)
        self.checkForBrokenLinks(body, '/++apidoc++/Code/menu.html',
                                 basic='mgr:mgrpw')

    def testMenuCodeFinder(self):
        response = self.publish('/++apidoc++/Code/menu.html',
                                basic='mgr:mgrpw',
                                form={'path': 'Code', 'SUBMIT': 'Find'})
        self.assertEqual(response.getStatus(), 200)
        body = response.getBody()
        self.assertIn(
            'zope.app.apidoc.codemodule.codemodule.CodeModule', body)
        self.checkForBrokenLinks(body, '/++apidoc++/Code/menu.html',
                                 basic='mgr:mgrpw')

    def testModuleDetailsView(self):
        response = self.publish('/++apidoc++/Code/zope/app/apidoc/apidoc',
                                basic='mgr:mgrpw')
        self.assertEqual(response.getStatus(), 200)
        body = response.getBody()
        self.assertIn('Zope 3 API Documentation', body)
        self.checkForBrokenLinks(
            body, '/++apidoc++/Code/zope/app/apidoc/apidoc', basic='mgr:mgrpw')

    def testClassDetailsView(self):
        response = self.publish(
            '/++apidoc++/Code/zope/app/apidoc/apidoc/APIDocumentation',
            basic='mgr:mgrpw')
        self.assertEqual(response.getStatus(), 200)
        body = response.getBody()
        self.assertIn('The collection of all API documentation', body)
        self.checkForBrokenLinks(
            body, '/++apidoc++/Code/zope/app/apidoc/apidoc/APIDocumentation',
            basic='mgr:mgrpw')

    def testFunctionDetailsView(self):
        response = self.publish(
            '/++apidoc++/Code/zope/app/apidoc/apidoc/handleNamespace',
            basic='mgr:mgrpw')
        self.assertEqual(response.getStatus(), 200)
        body = response.getBody()
        self.assertIn('handleNamespace(ob, name)', body)
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


class TestClass(unittest.TestCase):

    layer = APIDocLayer

    @unittest.skipIf(OOBTree.OOBTree is OOBTree.OOBTreePy,
                     "Only in the C implementation")
    def test_listClasses_C(self):
        from zope.app.apidoc.codemodule.browser.class_ import ClassDetails
        from zope.publisher.browser import TestRequest
        # BTree items doesn't set a module.

        items_class = type(OOBTree.OOBTree({1: 2}).items())

        details = ClassDetails()
        details.request = TestRequest()
        details.context = traverse(self.layer.getRootFolder(), '/++apidoc++')

        info = details._listClasses([items_class])
        self.assertIsNone(info[0]['url'], None)

    def test_not_fail_with_doc_property(self):
        from zope.app.apidoc.codemodule.browser.class_ import ClassDetails
        from zope.app.apidoc.codemodule.class_ import Class

        # Such as in zope.hookable._py_hookable
        class WithProperty(object):
            @property
            def __doc__(self):
                return "Some Docs"

        class Parent(object):
            def getPath(self):
                return '/'

        details = ClassDetails()
        details.context = Class(Parent(), WithProperty.__name__, WithProperty)

        self.assertIn('Failed to render non-text', details.getDoc())


class TestIntrospectorNS(unittest.TestCase):

    def _check_namespace(self, kind, context, name):
        from zope.app.apidoc.codemodule.browser import introspector
        from zope.location import LocationProxy

        namespace = getattr(introspector, kind + 'Namespace')
        traverser = namespace(context)
        obj = traverser.traverse(name, ())
        self.assertIsInstance(obj, LocationProxy)

        self.assertIs(obj.__parent__, context)
        self.assertTrue(obj.__name__.endswith(name))
        return traverser, obj

    def test_annotations(self):
        from zope.annotation.attribute import AttributeAnnotations
        anot = AttributeAnnotations(self)
        anot['key'] = 42
        self._check_namespace('annotations', anot, 'key')

    def test_items(self):
        self._check_namespace('sequenceItems', ["value"], '0')

    def test_mapping(self):
        self._check_namespace('mappingItems', {'key': 'value'}, 'key')


class TestIntrospector(unittest.TestCase):
    layer = APIDocLayer

    classAttr = 1

    def testIntrospector(self):
        from zope.app.apidoc.codemodule.browser.introspector import Introspector
        from zope.publisher.browser import TestRequest

        ispect = Introspector(self, TestRequest())
        atts = list(ispect.getAttributes())
        names = [x['name'] for x in atts]
        self.assertIn('classAttr', names)
        self.assertNotIn('testAttributes', names)


def test_suite():
    return unittest.TestSuite((
        LayerDocFileSuite(
            'README.rst',
            zope.app.apidoc.codemodule.browser),
        LayerDocTestSuite(
            'zope.app.apidoc.codemodule.browser.menu'),
        LayerDocFileSuite(
            "introspector.rst",
            zope.app.apidoc.codemodule.browser),
        unittest.defaultTestLoader.loadTestsFromName(__name__),
    ))

if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')
