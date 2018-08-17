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
"""Tests for the Interface Documentation Module

"""
import doctest
import os
import re
import sys
import unittest

import zope.app.renderer
import zope.component.testing
import zope.testing.module

from webtest import TestApp

from zope.app.apidoc.apidoc import APIDocumentation
from zope.app.apidoc.testing import APIDocLayer

from zope.app.component.testing import PlacefulSetup
from zope.app.component.testing import setUpTraversal

from zope.configuration import xmlconfig
from zope.interface import implementer
from zope.testing import renormalizing
from zope.traversing.interfaces import IContainmentRoot

_old_appsetup_context = None

def _setUp_AppSetup(filename='configure.zcml', execute=False):
    config_file = os.path.join(
        os.path.dirname(zope.app.apidoc.__file__), filename)

    # # Fix up path for tests.
    global _old_appsetup_context
    _old_appsetup_context = zope.app.appsetup.appsetup.getConfigContext()
    zope.app.appsetup.appsetup.__config_context = xmlconfig.file(
        config_file, zope.app.apidoc, execute=execute)

def _tearDown_AppSetup():
    global _old_appsetup_context
    zope.app.appsetup.appsetup.__config_context = _old_appsetup_context
    _old_appsetup_context = None



def _setUp_LayerPlace(test):
    # We're in the layer, so we don't want to tear down zope.testing,
    # which would tear down zope.component
    psetup = PlacefulSetup()
    # Make a folder tree and a site.
    psetup.buildFolders(True)
    root_folder = psetup.rootFolder
    setUpTraversal()

    global _old_appsetup_context
    _old_appsetup_context = zope.app.appsetup.appsetup.getConfigContext()
    zope.app.appsetup.appsetup.__config_context = APIDocLayer.context


    # Set up apidoc module
    test.globs['apidoc'] = APIDocumentation(root_folder, '++apidoc++')
    test.globs['rootFolder'] = root_folder

    from zope.app.apidoc.codemodule import codemodule
    codemodule._cleanUp()

def _tearDown_LayerPlace(test):
    _tearDown_AppSetup()


class BrowserTestCase(unittest.TestCase):

    layer = APIDocLayer

    def setUp(self):
        super(BrowserTestCase, self).setUp()
        _setUp_AppSetup()
        self._testapp = TestApp(self.layer.make_wsgi_app())

    def tearDown(self):
        _tearDown_AppSetup()
        super(BrowserTestCase, self).tearDown()


    def checkForBrokenLinks(self, orig_response, path,
                            basic=None, max_links=None):
        response = self.publish(path, basic=basic)
        links = response.html.find_all('a')

        seen = set()
        for link in links:
            try:
                href = link.attrs['href']
            except KeyError:
                pass

            if href.startswith('./'):
                href = href[2:]

            if href.startswith('http://localhost/'):
                href = href[16:]

            if not href.startswith('/'):
                href = path.rsplit('/', 1)[0] + '/' + href

            if href in seen:
                continue
            seen.add(href)

            self.publish(href, basic=basic)

            if max_links is not None:
                max_links -= 1
                if not max_links:
                    break

    def publish(self, path, basic=None, form=None, headers=None, env=None):
        assert basic
        self._testapp.authorization = ('Basic', tuple(basic.split(':')))
        env = env or {}
        env['wsgi.handleErrors'] = False
        if form:
            response = self._testapp.post(path, params=form,
                                          extra_environ=env, headers=headers)
        else:
            response = self._testapp.get(path, extra_environ=env, headers=headers)

        response.getBody = lambda: response.unicode_normal_body
        response.getStatus = lambda: response.status_int
        response.getHeader = lambda n: response.headers[n]
        return response



def setUp(test):
    zope.component.testing.setUp()
    xmlconfig.file('configure.zcml', zope.app.renderer)
    zope.testing.module.setUp(test, 'zope.app.apidoc.doctest')

def tearDown(test):
    zope.component.testing.tearDown()
    zope.testing.module.tearDown(test, 'zope.app.apidoc.doctest')


class TestPresentation(unittest.TestCase):

    def test_iconviewfactory(self):
        from zope.browserresource.icon import IconViewFactory
        from .presentation import getViewFactoryData
        factory = IconViewFactory('rname', 'alt', 0, 0)

        data = getViewFactoryData(factory)
        self.assertEqual(data['resource'], factory.rname)

class TestUtilities(unittest.TestCase):

    # All four implementations (Py2, PyPy2, Python 3, PyPy3) do different
    # things with slot method descriptors
    @unittest.skipIf(str is not bytes or hasattr(sys, 'pypy_version_info'),
                     "Only on CPython2")
    def test_slot_methods2(self):
        from zope.app.apidoc.utilities import getFunctionSignature
        self.assertEqual("(<unknown>)", getFunctionSignature(object.__init__))

    @unittest.skipIf(str is bytes or hasattr(sys, 'pypy_version_info'),
                     "Only on CPython3")
    def test_slot_methods3(self):
        from zope.app.apidoc.utilities import getFunctionSignature
        self.assertEqual(
            '(self, /, *args, **kwargs)',
            getFunctionSignature(object.__init__))

    @unittest.skipIf(str is not bytes or not hasattr(sys, 'pypy_version_info'),
                     "Only on PyPy2")
    def test_slot_methodspypy2(self): # pragma: no cover (we don't run coverage on pypy)
        from zope.app.apidoc.utilities import getFunctionSignature
        self.assertEqual("(obj, *args, **keywords)", getFunctionSignature(object.__init__))


    @unittest.skipUnless(str is bytes, "Only on py2")
    def test_unpack_methods(self):
        from zope.app.apidoc.utilities import getFunctionSignature
        import six

        six.exec_("def f((a, b)): pass")

        self.assertEqual("((a, b))", getFunctionSignature(locals()['f']))

    def test_keyword_only_arguments(self):
        from zope.app.apidoc.utilities import getFunctionSignature
        from zope.app.apidoc.utilities import _simpleGetFunctionSignature
        from socket import socket


        try:
            simple_sig = _simpleGetFunctionSignature(socket.makefile)
        except ValueError:
            # On Python 3, socket.makefile has keyword args, which aren't handled
            # by the simple function
            self.assertGreater(sys.version_info, (3,0))
            self.assertEqual(
                "(self, mode='r', buffering=None, *, encoding=None, errors=None, newline=None)",
                getFunctionSignature(socket.makefile))
            self.assertEqual(
                "(mode='r', buffering=None, *, encoding=None, errors=None, newline=None)",
                getFunctionSignature(socket.makefile, ignore_self=True))
            # Extra coverage to make sure the alternate branches are taken
            self.assertEqual(
                '()',
                getFunctionSignature(self.test_keyword_only_arguments))
            self.assertEqual(
                '(self)',
                # Note the difference with Python 2; this is what ignore_self
                # is for.
                getFunctionSignature(TestUtilities.test_keyword_only_arguments))
        else:
            self.assertEqual(simple_sig, "(mode='r', bufsize=-1)")
            # Extra coverage to make sure the alternate branches are taken
            self.assertEqual(
                '()',
                getFunctionSignature(self.test_keyword_only_arguments))
            self.assertEqual(
                '()',
                getFunctionSignature(TestUtilities.test_keyword_only_arguments))

    def test_renderText_non_text(self):
        # If we pass something that isn't actually text, we get a
        # descriptive error back.
        from zope.app.apidoc.utilities import renderText

        text = renderText(self)
        self.assertIn("Failed to render non-text", text)

    def test__qualname__descriptor_path(self):
        # When the __qualname__ is not a string but a descriptor object,
        # getPythonPath does not raise an AttributeError
        # https://github.com/zopefoundation/zope.app.apidoc/issues/25

        from zope.app.apidoc.utilities import getPythonPath

        class O(object):
            "namespace object"

        o = O()
        o.__qualname__ = object()
        o.__name__ = 'foo'

        self.assertEqual('zope.app.apidoc.tests.foo', getPythonPath(o))

    def test__qualname__descriptor_referencable(self):
        # When the __qualname__ is not a string but a descriptor object,
        # isReferencable does not raise an AttributeError
        # https://github.com/zopefoundation/zope.app.apidoc/issues/25

        from zope.app.apidoc import utilities

        # Set up an object that will return itself when looked up
        # as a module attribute via patching safe_import and when
        # asked for its __class__ so we can control the __qualname__
        # on all versions of Python.

        class O(object):
            "namespace object"

            def __getattribute__(self, name):
                if name in object.__getattribute__(self, '__dict__'):
                    return object.__getattribute__(self, '__dict__')[name]
                return self

        o = O()
        o.__qualname__ = object()

        def safe_import(path):
            return o

        old_safe_import = utilities.safe_import
        utilities.safe_import = safe_import
        try:
            self.assertTrue(utilities.isReferencable('a.module.object'))
        finally:
            utilities.safe_import = old_safe_import


from zope.app.apidoc import static

class TestStatic(unittest.TestCase):

    def _tempdir(self):
        import tempfile
        import shutil
        tmpdir = tempfile.mkdtemp(suffix='.apidoc.TestStatic')
        self.addCleanup(shutil.rmtree, tmpdir)
        return tmpdir

    def test_run(self):
        tmpdir = self._tempdir()
        static.main(['--max-runtime', '10', os.path.join(tmpdir, 'dir')])

        self.assertIn('static.html',
                      os.listdir(os.path.join(tmpdir, 'dir', '++apidoc++')))

    def test_run_404(self):
        tmpdir = self._tempdir()
        # Fetch a 404 page
        bad_url = '/++apidoc++/Code/zope/formlib/form/PageEditForm/index.html'
        maker = static.main(['--max-runtime', '10', # allow for old slow pypy
                             '--startpage', bad_url,
                             tmpdir])
        self.assertEqual(9, maker.counter) # our six default images, plus scripts
        self.assertEqual(1, maker.linkErrors)

    def test_custom_zcml(self):
        # This test uses the ZCML directive list to determine if a custom ZCML file was successfully loaded

        tmpdir = self._tempdir()
        directive = 'fakeModuleImport'
        package_name = 'zope.app.apidoc'
        zcml_file = 'test.zcml'

        # Make sure the directive isn't listed by default
        static.main(['--max-runtime', '10', os.path.join(tmpdir, 'default')])
        with open(os.path.join(tmpdir, 'default', '++apidoc++/ZCML/@@staticmenu.html')) as document:
            self.assertNotIn(directive, document.read())

        # Make sure that the directive is listed when we specify our custom ZCML file
        static.main(['--max-runtime', '10', os.path.join(tmpdir, 'custom'), '-c', '%s:%s' % (package_name, zcml_file)])
        with open(os.path.join(tmpdir, 'custom', '++apidoc++/ZCML/@@staticmenu.html')) as document:
            self.assertIn(directive, document.read(), "The %s directive isn't listed in zcmlmodule" % directive)

    def test_processLink_errors(self):
        tmpdir = self._tempdir()

        class ErrorBrowser(object):
            error_kind = ValueError
            contents = ''
            isHtml = False
            def open(self, url):
                raise self.error_kind(url)

        class ErrorGenerator(static.StaticAPIDocGenerator):
            error_kind = ValueError

            def processLink(self, link):
                b = self.browser
                self.browser = ErrorBrowser()
                self.browser.error_kind = self.error_kind
                super(ErrorGenerator, self).processLink(link)
                self.browser = b

        maker = static.main(['--max-runtime', '10', os.path.join(tmpdir, 'dir')],
                            generator=ErrorGenerator)
        self.assertEqual(7, maker.counter)
        self.assertEqual(7, maker.linkErrors)


        class BadErrorGenerator(ErrorGenerator):
            error_kind = Exception

        maker = static.main(['--max-runtime', '10', os.path.join(tmpdir, 'dir')],
                            generator=BadErrorGenerator)
        self.assertEqual(7, maker.counter)
        self.assertEqual(0, maker.linkErrors)
        self.assertEqual(7, maker.otherErrors)

    def test_cleanURL(self):
        self.assertEqual("http://localhost/",
                         static.cleanURL("http://localhost/#frogment"))

    def test_completeURL(self):
        self.assertEqual("http://localhost/index.html",
                         static.completeURL("http://localhost/"))

    def test_Link_localURL(self):

        self.assertFalse(static.Link('javascript:alert()', '').isLocalURL())
        self.assertFalse(static.Link('mailto:person@company', '').isLocalURL())
        self.assertFalse(static.Link("http://external.site/", "http://localhost/").isLocalURL())

    def test_OnlineBrowser(self):
        browser = static.OnlineBrowser.begin()
        browser.setUserAndPassword('user', 'password')
        # pylint:disable=protected-access
        x = browser._req_headers["Authorization"]
        self.assertEqual(x, 'Basic dXNlcjpwYXNzd29yZA==')
        browser.setDebugMode(True)
        x = browser._req_headers["X-zope-handle-errors"]
        self.assertEqual(x, 'False')

        browser.end()

    def test_mutually_exclusive_group(self):
        tmpdir = self._tempdir()

        with self.assertRaises(SystemExit):
            static._create_arg_parser().parse_args([tmpdir, '--publisher', '---custom-publisher', 'fake'])

        with self.assertRaises(SystemExit):
            static._create_arg_parser().parse_args([tmpdir, '-publisher', '--webserver'])

        with self.assertRaises(SystemExit):
            static._create_arg_parser().parse_args([tmpdir, '--webserver', '--custom-publisher', 'fake'])


# Generally useful classes and functions

@implementer(IContainmentRoot)
class Root(object):

    __parent__ = None
    __name__ = ''

standard_checker_patterns = (
    (re.compile(r"u('[^']*')"), r"\1"),
    (re.compile(r"b('[^']*')"), r"\1"),
    (re.compile("__builtin__"), 'builtins'),
    # repr of old style class is different on py2
    (re.compile("<class zope.app.apidoc.doctest.B.*>"),
     "<class 'zope.app.apidoc.doctest.B'>"),
    # there are no unbound methods on python 3
    (re.compile("<unbound method ([^>]*)>"),
     r"<function \1 at 0xabc>")
)

def standard_checker(*extra_patterns):
    return renormalizing.RENormalizing(standard_checker_patterns + extra_patterns)

standard_option_flags = (doctest.NORMALIZE_WHITESPACE
                         | doctest.ELLIPSIS
                         | renormalizing.IGNORE_EXCEPTION_MODULE_IN_PYTHON2)

def LayerDocFileSuite(filename, package):
    test = doctest.DocFileSuite(
        filename,
        package=package,
        setUp=_setUp_LayerPlace,
        tearDown=_tearDown_LayerPlace,
        checker=standard_checker(),
        optionflags=standard_option_flags)
    test.layer = APIDocLayer
    return test

def LayerDocTestSuite(modulename):
    test = doctest.DocTestSuite(
        modulename,
        setUp=_setUp_LayerPlace,
        tearDown=_tearDown_LayerPlace,
        checker=standard_checker(),
        optionflags=standard_option_flags)
    test.layer = APIDocLayer
    return test

def test_suite():
    checker = standard_checker()

    def file_test(name, **kwargs):
        return doctest.DocFileSuite(
            name,
            setUp=setUp,
            tearDown=tearDown,
            checker=checker,
            optionflags=standard_option_flags,
            **kwargs)

    return unittest.TestSuite((
        doctest.DocTestSuite('zope.app.apidoc.browser.apidoc',
                             setUp=setUp, tearDown=tearDown),
        file_test('README.rst'),
        file_test('classregistry.rst'),
        file_test('interface.rst'),
        file_test('component.rst'),
        file_test('presentation.rst',
                  globs={'__file__': __file__}),
        file_test('utilities.rst'),
        unittest.defaultTestLoader.loadTestsFromName(__name__),
    ))

if __name__ == '__main__':
    unittest.main(defaultTest="test_suite")
