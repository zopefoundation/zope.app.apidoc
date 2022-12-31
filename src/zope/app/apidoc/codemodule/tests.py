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
import doctest
import os.path
import unittest

from zope.component import testing

import zope.app.apidoc.codemodule
from zope.app.apidoc.codemodule.module import Module
from zope.app.apidoc.codemodule.text import TextFile
from zope.app.apidoc.tests import LayerDocFileSuite
from zope.app.apidoc.tests import standard_option_flags


here = os.path.dirname(__file__)


class TestText(unittest.TestCase):

    def _read_via_text(self, path):
        return TextFile(os.path.join(here, path), path, None).getContent()

    def _read_bytes(self, path):
        with open(os.path.join(here, path), 'rb') as f:
            return f.read()

    def test_crlf(self):
        self.assertEqual(self._read_bytes('_test_crlf.txt'),
                         b'This file\r\nuses \r\nWindows \r\nline endings.')

        self.assertEqual(self._read_via_text('_test_crlf.txt'),
                         'This file\nuses \nWindows \nline endings.')

    def test_cr(self):
        self.assertEqual(self._read_bytes('_test_cr.txt'),
                         b'This file\ruses \rMac \rline endings.')

        self.assertEqual(self._read_via_text('_test_cr.txt'),
                         'This file\nuses \nMac \nline endings.')


class TestModule(unittest.TestCase):

    def test_non_dir_on_path(self):
        path = zope.app.apidoc.codemodule.__path__
        zope.app.apidoc.codemodule.__path__ = ['this is not a path']
        try:
            mod = Module(None, 'codemodule', zope.app.apidoc.codemodule)
            self.assertEqual(0, len(mod))
        finally:
            zope.app.apidoc.codemodule.__path__ = path

    def test_idempotent(self):
        mod = Module(None, 'codemodule', zope.app.apidoc.codemodule)
        before = len(mod)
        self.assertGreater(before, 0)
        self.assertTrue(mod._package)
        mod._Module__needsSetup = True
        mod._Module__setup()
        self.assertEqual(len(mod), before)

    def test__all_invalid(self):
        assert not hasattr(zope.app.apidoc.codemodule, '__all__')
        zope.app.apidoc.codemodule.__all__ = ('missingname',)
        try:
            mod = Module(None, 'codemodule', zope.app.apidoc.codemodule)
            self.assertNotIn('missingname', mod)
            self.assertGreaterEqual(len(mod), 12)
        finally:
            del zope.app.apidoc.codemodule.__all__

    def test_access_attributes(self):
        mod = Module(None, 'codemodule', zope.app.apidoc.codemodule.tests)
        self.assertEqual(here, mod['here'])
        self.assertEqual(mod['here'].__name__, 'here')

    def test_hookable(self):
        import zope.component._api
        from zope.hookable import hookable
        self.assertIsInstance(zope.component._api.getSiteManager, hookable)
        from zope.app.apidoc.codemodule.function import Function
        mod = Module(None, 'hooks', zope.component._api)
        self.assertIsInstance(mod._children['getSiteManager'], Function)

    def test_zope_loaded_correctly(self):
        # Zope is guaranteed to be a namespace package, as is zope.app.
        import zope.annotation

        import zope
        import zope.app
        import zope.app.apidoc
        mod = Module(None, 'zope', zope)
        self.assertEqual(mod['annotation']._module, zope.annotation)
        self.assertEqual(mod['app']._module, zope.app)
        self.assertEqual(mod['app']['apidoc']._module, zope.app.apidoc)

    def test_module_with_file_of_none(self):
        # Sometimes namespace packages have this,
        # especially on Python 3.7.
        class Mod:
            __file__ = None
            __name__ = 'name'
            __package__ = None

        mod = Mod()
        mod.__doc__ = 'A module'

        inst = Module(None, 'name', mod)
        self.assertEqual(mod.__doc__, inst.getDocString())


class TestCodeModule(unittest.TestCase):

    def test_find_builtins(self):
        # CodeModule can always find builtins
        # root modules.
        import zope.app.apidoc.codemodule.codemodule
        cm = zope.app.apidoc.codemodule.codemodule.CodeModule()
        self.assertIsNotNone(cm.get('builtins'))

    def test_not_find_logging(self):
        # CodeModule other unregistered root modules,
        # like logging, are not implicitly found.
        import zope.app.apidoc.codemodule.codemodule
        cm = zope.app.apidoc.codemodule.codemodule.CodeModule()
        self.assertIsNone(cm.get('logging'))


class TestZCML(unittest.TestCase):

    def setUp(self):
        from zope.app.apidoc.tests import _setUp_AppSetup
        _setUp_AppSetup()

    def tearDown(self):
        from zope.app.apidoc.tests import _tearDown_AppSetup
        _tearDown_AppSetup()

    def test_installed(self):
        from zope.app.apidoc.codemodule.zcml import MyConfigHandler
        handler = MyConfigHandler(None)
        self.assertTrue(handler.evaluateCondition('installed zope'))
        self.assertFalse(handler.evaluateCondition('installed not-a-package'))

    def test_copy_with_root(self):
        from zope.app.apidoc.codemodule.zcml import ZCMLFile
        fname = os.path.join(here, '..', 'ftesting-base.zcml')
        zcml = ZCMLFile(fname, zope.app.apidoc,
                        None, None)

        zcml.rootElement
        self.assertEqual(zcml, zcml.rootElement.__parent__)

        clone = zcml.withParentAndName(self, 'name')
        self.assertEqual(clone.rootElement.__parent__, clone)


class TestClass(unittest.TestCase):

    def test_permission_is_not_method(self):
        # We don't incorrectly assume that callable objects,
        # like security proxies, are methods
        from zope.security.checker import CheckerPublic

        from zope.app.apidoc.codemodule.class_ import Class

        self.assertTrue(callable(CheckerPublic))

        class Parent:
            def getPath(self):
                return ''

        class MyClass:
            permission = CheckerPublic

        klass = Class(Parent(), MyClass.__name__, MyClass)

        self.assertEqual([], klass.getMethods())


def test_suite():
    return unittest.TestSuite((
        LayerDocFileSuite(
            'README.rst',
            zope.app.apidoc.codemodule),
        doctest.DocFileSuite(
            'directives.rst',
            setUp=testing.setUp,
            tearDown=testing.tearDown,
            optionflags=standard_option_flags),
        unittest.defaultTestLoader.loadTestsFromName(__name__),
    ))
