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
"""Class Documentation Module Views

$Id$
"""
__docformat__ = 'restructuredtext'
import inspect
import os
import re
from types import TypeType, ClassType, FunctionType, ModuleType
import xml.dom.minidom
import xml.sax.saxutils

from zope.configuration import docutils, xmlconfig
from zope.configuration.config import ConfigurationContext
from zope.configuration.fields import GlobalObject, Tokens
from zope.exceptions import NotFoundError
from zope.interface import implementedBy
from zope.interface.interface import InterfaceClass
from zope.schema import getFieldsInOrder
from zope.security.proxy import removeSecurityProxy

import zope.app
from zope.app import zapi
from zope.app.i18n import ZopeMessageIDFactory as _
from zope.app.apidoc.classmodule import Module, Class, Function, ZCMLFile
from zope.app.apidoc.classmodule import classRegistry
from zope.app.apidoc.interfaces import IDocumentationModule
from zope.app.apidoc.utilities import getPythonPath, renderText, columnize
from zope.app.apidoc.utilities import getPermissionIds, getFunctionSignature
from zope.app.apidoc.utilities import getPublicAttributes
from zope.app.apidoc.utilities import getInterfaceForAttribute
from zope.app.apidoc.zcmlmodule import quoteNS


class Menu(object):
    """Menu for the Class Documentation Module.

    The menu allows for looking for classes by partial names. See
    `findClasses()` for the simple search implementation.
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
        results.sort(lambda x, y: cmp(x['path'], y['path']))
        return results


_obj_attr_re = r'(?P<start>&lt;%s.*?%s=".*?)(?P<value>%s)(?P<end>".*?&gt;)'
_attrname_re = r'(?P<start>&lt;.*?%s.*?)(?P<attr>%s)(?P<end>=".*?".*?&gt;)'
directives = {}

class ZCMLFileDetails(ConfigurationContext):
    """Represents the details of the ZCML file."""

    def __init__(self, context, request):
        self.context = context
        self.request = request
        # TODO: This is not the best way to do this. We really need to revisit
        # the entire implementation and move more to the ZCMLFile object.
        package = removeSecurityProxy(
            zapi.getParent(context))._Module__module
        # Keep track of the package that is used for relative paths
        self._package_stack = [package]
        # Keep track of completed actions, so none is executed twice
        self._done = []
        # Kepp track of the parent node, so that we know whether we deal with
        # a directive or sub-directive 
        self._parent_node_info = None

    # See zope.configuration.config.ConfigurationContext
    # The package is used to resolve relative paths.
    package = property(lambda self: self._package_stack[-1])

    # All registered directives. The availability of directives depends on
    # whether we a re looking for a directive or a sub-directive.
    directives = property(lambda self: directives[self._parent_node_info])

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

    def getHTMLContents(self):
        """Return an HTML markup version of the ZCML file with links to other
        documentation modules."""
        if not directives:
            self._makeDocStructure()
        dom = xml.dom.minidom.parse(self.context.path)
        self.text = file(self.context.path, 'r').read()
        self.text = xml.sax.saxutils.escape(self.text)
        self.text = self.text.replace(' ', '&nbsp;')
        self.text = self.text.replace('\n', '<br />\n')

        # Link interface and other object references
        for node in dom.childNodes:
            self._linkObjectReferences(node)

        # Link ZCML directives
        for node in dom.childNodes:
            self._linkDirectives(node)

        # Color directive attributes
        for node in dom.childNodes:
            self._colorAttributeNames(node)

        # Color comments
        self._colorComments()
        
        return self.text

    def _colorComments(self):
        self.text = self.text.replace('&lt;!--',
                                      '<span style="color: red">&lt;!--')
        self.text = self.text.replace('--&gt;',
                                      '--&gt;</span>')

    def _colorAttributeNames(self, node):
        if node.nodeType in (node.TEXT_NODE, node.COMMENT_NODE):
            return

        for attrName in node.attributes.keys():
            disc = ('color attribute name', node.tagName, attrName)
            if disc in self._done:
                continue

            expr = re.compile(_attrname_re %(node.tagName, attrName),
                              re.DOTALL)
            self.text = re.sub(
                expr,
                r'\1<span class="attribute">\2</span>\3',
            self.text)
            
            self._done.append(disc)

        for child in node.childNodes:
            self._colorAttributeNames(child)


    def _linkDirectives(self, node):
        if node.nodeType in (node.TEXT_NODE, node.COMMENT_NODE):
            return

        if (node.tagName,) in self._done:
            return

        if node.namespaceURI in self.directives.keys() and \
               node.localName in self.directives[node.namespaceURI].keys():
            namespace = quoteNS(node.namespaceURI)
        else:
            namespace = 'ALL'

        self.text = self.text.replace(
            '&lt;'+node.tagName,
            '&lt;<a class="tagname" href="%s/ZCML/%s/%s/index.html">%s</a>' %(
            self.getBaseURL(), namespace, node.localName, node.tagName))

        self.text = self.text.replace(
            '&lt;/'+node.tagName+'&gt;',
            '&lt;/<a class="tagname" '
            'href="%s/ZCML/%s/%s/index.html">%s</a>&gt;' %(
            self.getBaseURL(), namespace, node.localName, node.tagName))

        self._done.append((node.tagName,))
        
        for child in node.childNodes:
            self._linkDirectives(child)


    def _linkObjectReferences(self, node):
        if node.nodeType in (node.TEXT_NODE, node.COMMENT_NODE):
            return

        if node.localName == 'configure' and node.hasAttribute('package'):
            self._package_stack.push(
                self.resolve(node.getAttribute('package')))

        for child in node.childNodes:
            self._linkObjectReferences(child)

        namespace = self.directives.get(node.namespaceURI, self.directives[''])
        directive = namespace.get(node.localName)
        if directive is None:
            # Try global namespace
            directive = self.directives[''].get(node.localName)

        for name, field in getFieldsInOrder(directive[0]):
            if node.hasAttribute(name.strip('_')):
                self._evalField(field, node)

        if node.localName == 'configure' and node.hasAttribute('package'):
            self._package_stack.pop()


    def _evalField(self, field, node, attrName=None, dottedName=None):
        bound = field.bind(self)
        if attrName is None:
            attrName = field.getName().strip('_')
        if dottedName is None:
            dottedName = node.getAttribute(attrName)

        if isinstance(field, Tokens) and \
               isinstance(field.value_type, GlobalObject):
                       
            tokens = [token.strip()
                      for token in node.getAttribute(attrName).split(' \n\t')
                      if token.strip() != '']

            for token in tokens:
                self._evalField(field.value_type, node, attrName, dottedName)

        if isinstance(field, GlobalObject):
            obj = bound.fromUnicode(dottedName)
            disc = (node.tagName, attrName, dottedName)

            if disc in self._done:
                return

            if isinstance(obj, InterfaceClass):
                expr = re.compile(_obj_attr_re %(
                    node.tagName, attrName, dottedName.replace('.', r'\.')),
                                  re.DOTALL)                
                path = obj.__module__ + '.' + obj.__name__
                self.text = re.sub(
                    expr,
                    r'\1<a class="objectref" '
                    r'href="%s/Interface/%s/apiindex.html">\2</a>\3' %(
                    self.getBaseURL(), path),
                    self.text)

            elif isinstance(obj, (TypeType, ClassType, FunctionType)):
                expr = re.compile(_obj_attr_re %(
                    node.tagName, attrName, dottedName.replace('.', r'\.')),
                                  re.DOTALL)
                path = (obj.__module__ + '.' + obj.__name__).replace('.', '/')
                self.text = re.sub(
                    expr,
                    r'\1<a class="objectref" '
                    r'href="%s/Class/%s/index.html">\2</a>\3' %(
                    self.getBaseURL(), path),
                    self.text)

            elif isinstance(obj, ModuleType):
                expr = re.compile(_obj_attr_re %(
                    node.tagName, attrName, dottedName.replace('.', r'\.')),
                                  re.DOTALL)
                path = obj.__name__.replace('.', '/')
                self.text = re.sub(
                    expr,
                    r'\1<a class="objectref" '
                    r'href="%s/Class/%s/index.html">\2</a>\3' %(
                    self.getBaseURL(), path),
                    self.text)

            self._done.append(disc)
                        
    def _makeDocStructure(self):
        # Some trivial caching
        global directives
        context = xmlconfig.file(
            zope.app.appsetup.appsetup.getConfigSource(),
            execute=False)
        namespaces, subdirs = docutils.makeDocStructures(context)

        for ns_name, dirs in namespaces.items():
            for dir_name, dir in dirs.items():
                parent = directives.setdefault(None, {})
                namespace = parent.setdefault(ns_name, {})
                namespace[dir_name] = dir

        for parent_info, dirs in subdirs.items():
            for dir in dirs:
                parent = directives.setdefault(parent_info, {})
                namespace = parent.setdefault(dir[0], {})
                namespace[dir[1]] = dir[2:]


class FunctionDetails(object):
    """Represents the details of the function."""

    def getDocString(self):
        r"""Get the doc string of the function in a rendered format.

        Example::

          >>> from tests import getFunctionDetailsView
          >>> view = getFunctionDetailsView()

          >>> view.getDocString()
          u'<p>This is the foo function.</p>\n'
        """
        return renderText(self.context.getDocString() or '',
                          zapi.getParent(self.context).getPath())


    def getAttributes(self):
        """Get all attributes of this function.

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
        return [{'name': name,
                 'value': `attr`,
                 'type': type(attr).__name__,
                 'type_link': _getTypePath(type(attr)).replace('.', '/')}
                
                for name, attr in self.context.getAttributes()]


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
            try:
                klass = zapi.traverse(classModule, path.replace('.', '/'))
                url = zapi.getView(klass, 'absolute_url', self.request)()
            except NotFoundError:
                # If one of the base classes is implemented in C, we will not
                # be able to find it.
                url = None
            info.append({'path': path, 'url': url})
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
           ('type', 'MessageID'),
           ('type_link', 'zope.i18nmessageid.messageid.MessageID'),
           ('value', "u'Classes'"),
           ('write_perm', None)]
        """
        attrs = []
        for name, attr, iface in self.context.getAttributes():
            entry = {'name': name,
                     'value': `attr`,
                     'type': type(attr).__name__,
                     'type_link': _getTypePath(type(attr)),
                     'interface': getPythonPath(iface)}
            # Since checkers do not have security declarations on their API,
            # we have to remove the security wrapper to get to the API calls. 
            checker = self.context.getSecurityChecker()
            entry.update(
                getPermissionIds(name, removeSecurityProxy(checker)))
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
          [[('doc', u''),
            ('interface',
             'zope.interface.common.mapping.IEnumerableMapping'),
            ('name', 'keys'),
            ('read_perm', None),
            ('signature', '()'),
            ('write_perm', None)],
           [('doc', u''),
            ('interface',
             'zope.interface.common.mapping.IEnumerableMapping'),
            ('name', 'values'),
            ('read_perm', None),
            ('signature', '()'),
            ('write_perm', None)]]
        """
        methods = []
        # remove the security proxy, so that `attr` is not proxied. We could
        # unproxy `attr` for each turn, but that would be less efficient.
        #
        # `getPermissionIds()` also expects the class's security checker not
        # to be proxied.
        klass = removeSecurityProxy(self.context)
        for name, attr, iface in klass.getMethods():
            entry = {'name': name,
                     'signature': getFunctionSignature(attr),
                     'doc': renderText(attr.__doc__ or '',
                                       zapi.getParent(self.context).getPath()),
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

          DISABLED due to differences in STX behavior between
          Zope 2.8 and Zope 3. Consequence of Five integration.
          #>>> print view.getDoc()[23:80]
          #<p>Represent the Documentation of any possible class.</p>
        """
        return renderText(self.context.getDocString() or '',
                          zapi.getParent(self.context).getPath())


class ModuleDetails(object):
    """Represents the details of the module."""

    def getDoc(self):
        """Get the doc string of the module STX formatted.

        Example::

          The class we are using for this view is zope.app.apidoc.classmodule.

          >>> from tests import getModuleDetailsView
          >>> view = getModuleDetailsView()

          DISABLED due to differences in STX behavior between
          Zope 2.8 and Zope 3. Consequence of Five integration.
          #>>> print view.getDoc().strip()
          #<div class="document">
          #<p>Class Documentation Module</p>
          #<p>This module is able to take a dotted name of any class and display
          #documentation for it.</p>
          #</div>
        """
        text = self.context.getDocString()
        if text is None:
            return None
        lines = text.strip().split('\n')
        # Get rid of possible CVS id.
        lines = [line for line in lines if not line.startswith('$Id')]
        return renderText('\n'.join(lines), self.context.getPath())

    def getEntries(self, columns=True):
        """Return info objects for all modules and classes in this module.

        Example::

          The class we are using for this view is zope.app.apidoc.classmodule.

          >>> from zope.app.apidoc.tests import pprint
          >>> from tests import getModuleDetailsView
          >>> view = getModuleDetailsView()

          >>> entries = view.getEntries(False)
          >>> entries.sort()
          >>> pprint(entries[1:3])
          [[('isclass', False),
            ('isfunction', False),
            ('ismodule', True),
            ('iszcmlfile', False),
            ('name', 'browser'),
            ('url', 'http://127.0.0.1/zope/app/apidoc/classmodule/browser')],
           [('isclass', False),
            ('isfunction', True),
            ('ismodule', False),
            ('iszcmlfile', False),
            ('name', 'cleanUp'),
            ('url', 'http://127.0.0.1/zope/app/apidoc/classmodule/cleanUp')]]
        """
        entries = [{'name': name,
                    'url': zapi.getView(obj, 'absolute_url', self.request)(),
                    'ismodule': zapi.isinstance(obj, Module),
                    'isclass': zapi.isinstance(obj, Class),
                    'isfunction': zapi.isinstance(obj, Function),
                    'iszcmlfile': zapi.isinstance(obj, ZCMLFile)}
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
          [[('url', 'http://127.0.0.1'), ('name', u'[top]')],
           [('url', 'http://127.0.0.1/zope'), ('name', 'zope')],
           [('url', 'http://127.0.0.1/zope/app'), ('name', 'app')],
           [('url', 'http://127.0.0.1/zope/app/apidoc'), ('name', 'apidoc')],
           [('url', 'http://127.0.0.1/zope/app/apidoc/classmodule'),
            ('name', 'classmodule')]]
        """
        names = self.context.getPath().split('.') 
        crumbs = []
        module = self.context
        # I really need the class here, so remove the proxy.
        while removeSecurityProxy(module).__class__ is Module:
            crumbs.append(
                {'name': zapi.name(module),
                 'url': zapi.getView(module, 'absolute_url', self.request)()}
                )
            module = zapi.getParent(module)

        crumbs.append(
            {'name': _('[top]'),
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
