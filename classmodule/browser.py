##############################################################################
#
# Copyright (c) 2004 Zope Corporation and Contributors.
# All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.0 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
##############################################################################
"""Class Documentation Module Views

$Id$
"""
import os
import inspect

from zope.interface import implementedBy
from zope.configuration.config import ConfigurationContext
from zope.proxy import removeAllProxies

from zope.app import zapi
from zope.app.apidoc.utilities import getPythonPath, stx2html, columnize
from zope.app.apidoc.utilities import getPermissionIds, getFunctionSignature
from zope.app.apidoc.utilities import getPublicAttributes
from zope.app.apidoc.utilities import getInterfaceForAttribute
from zope.app.apidoc.classmodule import Module, Class, Function, classRegistry
from zope.app.apidoc.interfaces import IDocumentationModule

class Menu(object):
    """Menu for the Class Documentation Module.

    The menu allows for looking for classes by partial names. See
    'findClasses()' for the simple search implementation.
    """

    def findClasses(self):
        """Find the classes that match a partial path.

        Examples::

          >>> from zope.app.apidoc.tests import pprint
          >>> from zope.app.apidoc.classmodule import Class
          >>> cm = zapi.getUtility(IDocumentationModule, 'Class')
          >>> mod = cm['zope']['app']['apidoc']['classmodule']['browser']

          Setup a couple of classes and register them.

          >>> class Foo(object):
          ...     pass
          >>> mod._Module__children['Foo'] = Class(mod, 'Foo', Foo)
          >>> class Foo2(object):
          ...     pass
          >>> mod._Module__children['Foo2'] = Class(mod, 'Foo2', Foo2)
          >>> class Blah(object):
          ...     pass
          >>> mod._Module__children['Blah'] = Class(mod, 'Blah', Blah)

          Setup the view.

          >>> from zope.publisher.browser import TestRequest
          >>> menu = Menu()
          >>> menu.context = None

          Testing the method with various inputs.
          
          >>> menu.request = TestRequest(form={'path': 'Foo'})
          >>> info = menu.findClasses()
          >>> pprint(info)
          [[('path', 'zope.app.apidoc.classmodule.browser.Foo'),
            ('url',
             'http://127.0.0.1/zope/app/apidoc/classmodule/browser/Foo')],
           [('path', 'zope.app.apidoc.classmodule.browser.Foo2'),
            ('url',
             'http://127.0.0.1/zope/app/apidoc/classmodule/browser/Foo2')]]

          >>> menu.request = TestRequest(form={'path': 'o2'})
          >>> info = menu.findClasses()
          >>> pprint(info)
          [[('path', 'zope.app.apidoc.classmodule.browser.Foo2'),
            ('url',
             'http://127.0.0.1/zope/app/apidoc/classmodule/browser/Foo2')]]

          >>> menu.request = TestRequest(form={'path': 'Blah'})
          >>> info = menu.findClasses()
          >>> pprint(info)
          [[('path', 'zope.app.apidoc.classmodule.browser.Blah'),
            ('url',
             'http://127.0.0.1/zope/app/apidoc/classmodule/browser/Blah')]]
        """
        path = self.request.get('path', None)
        if path is None:
            return []
        classModule = zapi.getUtility(IDocumentationModule, "Class")
        results = []
        for p in classRegistry.keys():
            if p.find(path) >= 0:
                klass = zapi.traverse(classModule, p.replace('.', '/'))
                results.append(
                    {'path': p,
                     'url': zapi.getView(klass, 'absolute_url', self.request)()
                     })
        return results

class FunctionDetails(object):
    """Represents the details of the function."""

    def getDocString(self):
        r"""Get the doc string of the class STX formatted.

        Example::

          >>> from tests import getFunctionDetailsView
          >>> view = getFunctionDetailsView()

          >>> view.getDocString()
          '<p>This is the foo function.</p>\n'
        """
        return stx2html(self.context.getDocString() or '', 3)


    def getAttributes(self):
        """Get all attributes of this class.

        Example::

          >>> from zope.app.apidoc.tests import pprint
          >>> from tests import getFunctionDetailsView
          >>> view = getFunctionDetailsView()

          >>> attr = view.getAttributes()[0]
          >>> pprint(attr)
          [('name', 'deprecated'),
           ('type', 'bool'),
           ('type_link', '__builtin__/bool'),
           ('value', 'True')]
        """
        attrs = []
        func = removeAllProxies(self.context)
        return [{'name': name,
                 'value': `attr`,
                 'type': type(attr).__name__,
                 'type_link': _getTypePath(type(attr)).replace('.', '/')}
                
                for name, attr in func.getAttributes()]


class ClassDetails(object):
    """Represents the details of the class."""

    def getBases(self):
        """Get all bases of this class.

        Example::

          The class we are using for this view is
          zope.app.apidoc.classmodule.ClassModule.

          >>> import pprint
          >>> from tests import getClassDetailsView
          >>> view = getClassDetailsView()

          >>> pprint.pprint(view.getBases())
          [{'path': 'zope.app.apidoc.classmodule.Module',
            'url': 'http://127.0.0.1/zope/app/apidoc/classmodule/Module'}]
        """
        info = []
        classModule = zapi.getUtility(IDocumentationModule, "Class")
        for base in self.context.getBases():
            path = getPythonPath(base)
            klass = zapi.traverse(classModule, path.replace('.', '/'))
            info.append(
                {'path': path,
                 'url': zapi.getView(klass, 'absolute_url',
                                     self.request)()})
        return info


    def getBaseURL(self):
        """Return the URL for the API Documentation Tool.

        Example::

          >>> from tests import getClassDetailsView
          >>> view = getClassDetailsView()

          Note that the following output is a bit different than usual, since
          we have not setup all path elements.

          >>> view.getBaseURL()
          'http://127.0.0.1'
        """
        m = zapi.getUtility(IDocumentationModule, "Class")
        return zapi.getView(zapi.getParent(m), 'absolute_url', self.request)()


    def getInterfaces(self):
        """Get all implemented interfaces (as paths) of this class.

        Example::

          The class we are using for this view is
          zope.app.apidoc.classmodule.ClassModule.

          >>> from zope.app.apidoc.tests import pprint
          >>> from tests import getClassDetailsView
          >>> view = getClassDetailsView()

          >>> pprint(view.getInterfaces())
          ['zope.app.apidoc.interfaces.IDocumentationModule',
           'zope.app.location.interfaces.ILocation',
           'zope.app.apidoc.classmodule.IModuleDocumentation',
           'zope.app.container.interfaces.IReadContainer']
        """
        return map(getPythonPath, self.context.getInterfaces())


    def getAttributes(self):
        """Get all attributes of this class.

        Example::

          The class we are using for this view is
          zope.app.apidoc.classmodule.ClassModule.

          >>> from zope.app.apidoc.tests import pprint
          >>> from tests import getClassDetailsView
          >>> view = getClassDetailsView()

          >>> attr = view.getAttributes()[2]
          >>> pprint(attr)
          [('interface', 'zope.app.apidoc.interfaces.IDocumentationModule'),
           ('name', 'title'),
           ('read_perm', None),
           ('type', 'str'),
           ('type_link', '__builtin__.str'),
           ('value', "'Classes'"),
           ('write_perm', None)]
        """
        attrs = []
        klass = removeAllProxies(self.context)
        for name, attr, iface in klass.getAttributes():
            entry = {'name': name,
                     'value': `attr`,
                     'type': type(attr).__name__,
                     'type_link': _getTypePath(type(attr)),
                     'interface': getPythonPath(iface)}
            checker = removeAllProxies(klass.getSecurityChecker())
            entry.update(getPermissionIds(name, checker))
            attrs.append(entry)
        return attrs


    def getMethods(self):
        """Get all methods of this class.

        Example::

          The class we are using for this view is
          zope.app.apidoc.classmodule.ClassModule.

          >>> from zope.app.apidoc.tests import pprint
          >>> from tests import getClassDetailsView
          >>> view = getClassDetailsView()

          >>> methods = view.getMethods()
          >>> pprint(methods[-2:])
          [[('doc', ''),
            ('interface',
             'zope.interface.common.mapping.IEnumerableMapping'),
            ('name', 'keys'),
            ('read_perm', None),
            ('signature', '()'),
            ('write_perm', None)],
           [('doc', ''),
            ('interface',
             'zope.interface.common.mapping.IEnumerableMapping'),
            ('name', 'values'),
            ('read_perm', None),
            ('signature', '()'),
            ('write_perm', None)]]
        """
        methods = []
        klass = removeAllProxies(self.context)
        for name, attr, iface in klass.getMethods():
            entry = {'name': name,
                     'signature': getFunctionSignature(attr),
                     'doc': stx2html(attr.__doc__ or '', 3),
                     'interface': getPythonPath(iface)}
            entry.update(getPermissionIds(name, klass.getSecurityChecker()))
            methods.append(entry)
        return methods


    def getDoc(self):
        """Get the doc string of the class STX formatted.

        Example::

          The class we are using for this view is
          zope.app.apidoc.classmodule.ClassModule.

          >>> from tests import getClassDetailsView
          >>> view = getClassDetailsView()

          >>> print view.getDoc()[:59]
          <h3>Represent the Documentation of any possible class.</h3>
        """
        return stx2html(self.context.getDocString() or '', 3)


class ModuleDetails(object):
    """Represents the details of the module."""

    def getDoc(self):
        """Get the doc string of the module STX formatted.

        Example::

          The class we are using for this view is zope.app.apidoc.classmodule.

          >>> from tests import getModuleDetailsView
          >>> view = getModuleDetailsView()

          >>> print view.getDoc().strip()
          <p>Class Documentation Module</p>
          <p>This module is able to take a dotted name of any class and display
          documentation for it.</p>
        """
        text = self.context.getDocString()
        if text is None:
            return None
        lines = text.strip().split('\n')
        # Get rid of possible CVS id.
        lines = [line for line in lines if not line.startswith('$Id')]
        return stx2html('\n'.join(lines), 3)

    def getEntries(self, columns=True):
        """Return info objects for all modules and classes in this module.

        Example::

          The class we are using for this view is zope.app.apidoc.classmodule.

          >>> from zope.app.apidoc.tests import pprint
          >>> from tests import getModuleDetailsView
          >>> view = getModuleDetailsView()

          >>> entries = view.getEntries(False)
          >>> entries.sort()
          >>> pprint(entries[:2])
          [[('isclass', False),
            ('isfunction', False),
            ('ismodule', True),
            ('name', 'browser'),
            ('url', 'http://127.0.0.1/zope/app/apidoc/classmodule/browser')],
           [('isclass', False),
            ('isfunction', True),
            ('ismodule', False),
            ('name', 'cleanUp'),
            ('url', 'http://127.0.0.1/zope/app/apidoc/classmodule/cleanUp')]]
        """
        entries = [{'name': name,
                    'url': zapi.getView(obj, 'absolute_url', self.request)(),
                    'ismodule': type(removeAllProxies(obj)) is Module,
                    'isclass': type(removeAllProxies(obj)) is Class,
                    'isfunction': type(removeAllProxies(obj)) is Function,}
                   for name, obj in self.context.items()]
        entries.sort(lambda x, y: cmp(x['name'], y['name']))
        if columns:
            entries = columnize(entries)
        return entries

    def getBreadCrumbs(self):
        """Create breadcrumbs for the module path.

        We cannot reuse the the system's bread crumbs, since they go all the
        way up to the root, but we just want to go to the root module.

        Example::

          >>> from zope.app.apidoc.tests import pprint
          >>> from tests import getModuleDetailsView
          >>> view = getModuleDetailsView()

          >>> crumbs = [crumb.items() for crumb in view.getBreadCrumbs()]
          >>> pprint(crumbs)
          [[('url', 'http://127.0.0.1'), ('name', '[top]')],
           [('url', 'http://127.0.0.1/zope'), ('name', 'zope')],
           [('url', 'http://127.0.0.1/zope/app'), ('name', 'app')],
           [('url', 'http://127.0.0.1/zope/app/apidoc'), ('name', 'apidoc')],
           [('url', 'http://127.0.0.1/zope/app/apidoc/classmodule'),
            ('name', 'classmodule')]]
        """
        names = self.context.getPath().split('.') 
        crumbs = []
        module = self.context
        while type(removeAllProxies(module)) is Module:
            crumbs.append(
                {'name': zapi.name(module),
                 'url': zapi.getView(module, 'absolute_url', self.request)()}
                )
            module = zapi.getParent(module)

        crumbs.append(
            {'name': '[top]',
             'url': zapi.getView(module, 'absolute_url', self.request)()} )

        crumbs.reverse()
        return crumbs


def _getTypePath(type):
    """Return the path of the type.

    Here some examples::

      >>> class Foo(object):
      ...     pass

      >>> _getTypePath(type(Foo()))
      'zope.app.apidoc.classmodule.browser.Foo'

      >>> _getTypePath(type(3))
      '__builtin__.int'
    """
    path = getPythonPath(type)
    return path
