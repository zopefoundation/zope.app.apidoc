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
import os.path
import unittest
import doctest

from zope.component import testing

from zope.app.apidoc.codemodule.text import TextFile
from zope.app.apidoc.codemodule.module import Module

from zope.app.apidoc.tests import standard_checker
from zope.app.apidoc.tests import standard_option_flags
from zope.app.apidoc.tests import LayerDocFileSuite
import zope.app.apidoc.codemodule

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
                         u'This file\nuses \nWindows \nline endings.')

    def test_cr(self):
        self.assertEqual(self._read_bytes('_test_cr.txt'),
                         b'This file\ruses \rMac \rline endings.')

        self.assertEqual(self._read_via_text('_test_cr.txt'),
                         u'This file\nuses \nMac \nline endings.')

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

def test_suite():
    checker = standard_checker()

    return unittest.TestSuite((
        LayerDocFileSuite(
            'README.rst',
            zope.app.apidoc.codemodule),
        doctest.DocFileSuite(
            'directives.rst',
            setUp=testing.setUp,
            tearDown=testing.tearDown,
            checker=checker,
            optionflags=standard_option_flags),
        unittest.defaultTestLoader.loadTestsFromName(__name__),
    ))

if __name__ == '__main__':
    unittest.main(defaultTest="test_suite")
