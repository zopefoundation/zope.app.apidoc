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
"""Browser Views for ZCML Reference

$Id$
"""
__docformat__ = 'restructuredtext'

from zope.configuration.xmlconfig import ParserInfo
from zope.security.proxy import removeSecurityProxy

from zope.app import zapi
from zope.app.location import LocationProxy
from zope.app.apidoc.zcmlmodule import Directive, Namespace
from zope.app.apidoc.ifacemodule.browser import InterfaceDetails
from zope.app.apidoc.utilities import getPythonPath, relativizePath

class Menu(object):
    """Menu View Helper Class

    Examples::

      >>> from zope.app.tree.node import Node 
      >>> from zope.app.apidoc.zcmlmodule import Namespace, Directive
      >>> from zope.app.apidoc.zcmlmodule import ZCMLModule
      >>> from zope.app.apidoc.tests import Root
      >>> menu = Menu()

      >>> module = ZCMLModule()
      >>> module.__parent__ = Root()
      >>> module.__name__ = 'ZCML'

      Namespace representing directives available in all namespaces.

      >>> ns = Namespace(module, 'ALL')
      >>> node = Node(ns)
      >>> menu.getMenuTitle(node)
      'All Namespaces'
      >>> menu.getMenuLink(node) is None
      True

      From now on we use the browser namespace.
      
      >>> ns = Namespace(module, 'http://namespaces.zope.org/browser')
      >>> node = Node(ns)
      >>> menu.getMenuTitle(node)
      'browser'
      >>> menu.getMenuLink(node) is None
      True

      The namespace has a page directive.

      >>> dir = Directive(ns, 'page', None, None, None, None)
      >>> node = Node(dir)
      >>> menu.getMenuTitle(node)
      'page'
      >>> menu.getMenuLink(node)
      './http_co__sl__sl_namespaces.zope.org_sl_browser/page/index.html'
    """

    def getMenuTitle(self, node):
        """Return the title of the node that is displayed in the menu."""
        obj = node.context
        if zapi.isinstance(obj, Namespace):
            name = obj.getShortName()
            if name == 'ALL':
                return 'All Namespaces'
            return name
        return zapi.name(obj)

    def getMenuLink(self, node):
        """Return the HTML link of the node that is displayed in the menu."""
        obj = node.context
        if zapi.isinstance(obj, Directive):
            ns = zapi.getParent(obj)
            return './'+zapi.name(ns) + '/' + zapi.name(obj) + '/index.html'
        return None


class DirectiveDetails(object):
    """View class for a Directive."""

    def getSchema(self):
        """Return the schema of the directive.

        Examples::
        
          >>> from zope.interface import Interface
          >>> from zope.publisher.browser import TestRequest
          >>> from tests import getDirective
          >>> details = DirectiveDetails()
          >>> details.context = getDirective()
          >>> details.request = TestRequest()

          >>> class IFoo(Interface):
          ...     pass
          >>> details.context.schema = IFoo
          >>> iface = details.getSchema()
          >>> if_class = iface.__class__
          >>> if_class.__module__ + '.' + if_class.__name__
          'zope.app.apidoc.ifacemodule.browser.InterfaceDetails'
          >>> iface.context
          <InterfaceClass zope.app.apidoc.zcmlmodule.browser.IFoo>
        """
        schema = LocationProxy(self.context.schema,
                               self.context,
                               getPythonPath(self.context.schema))
        details = InterfaceDetails()
        details.context = schema
        details.request = self.request
        return details

    def getNamespaceName(self):
        """Return the name of the namespace.

        Examples::

          >>> from tests import getDirective
          >>> details = DirectiveDetails()

          >>> details.context = getDirective()
          >>> details.getNamespaceName()
          'http://namespaces.zope.org/browser'

          >>> details.context.__parent__.__realname__ = 'ALL'
          >>> details.getNamespaceName()
          '<i>all namespaces</i>'
        """
        name = zapi.getParent(self.context).getFullName()
        if name == 'ALL':
            return '<i>all namespaces</i>'
        return name

    def getFileInfo(self):
        """Get the file where the directive was declared.

        Examples::
        
          >>> from zope.app.apidoc.tests import pprint
          >>> from zope.configuration.xmlconfig import ParserInfo
          >>> from tests import getDirective
          >>> details = DirectiveDetails()
          >>> details.context = getDirective()

          >>> details.getFileInfo() is None
          True

          >>> details.context.info = ParserInfo('foo.zcml', 2, 3)
          >>> info = details.getFileInfo()
          >>> pprint(info)
          [('column', 3),
           ('ecolumn', 3),
           ('eline', 2),
           ('file', 'foo.zcml'),
           ('line', 2)]
        """
        # ZCML directive `info` objects do not have security declarations, so
        # everything is forbidden by default. We need to remove the security
        # proxies in order to get to the data.  
        info = removeSecurityProxy(self.context.info)
        if zapi.isinstance(info, ParserInfo):
            return {'file': relativizePath(info.file),
                    'line': info.line,
                    'column': info.column,
                    'eline': info.eline,
                    'ecolumn': info.ecolumn}
        return None

    def getInfo(self):
        """Get the file where the directive was declared.

        Examples::
        
          >>> from zope.configuration.xmlconfig import ParserInfo
          >>> from tests import getDirective
          >>> details = DirectiveDetails()
          >>> details.context = getDirective()

          >>> details.getInfo() is None
          True

          >>> details.context.info = 'info here'
          >>> details.getInfo()
          'info here'

          >>> details.context.info = ParserInfo('foo.zcml', 2, 3)
          >>> details.getInfo() is None
          True
        """
        if isinstance(self.context.info, (str, unicode)):
            return self.context.info
        return None

    def getHandler(self):
        """Return information about the handler.

        Examples::
        
          >>> from zope.app.apidoc.tests import pprint
          >>> from zope.configuration.xmlconfig import ParserInfo
          >>> from tests import getDirective
          >>> details = DirectiveDetails()
          >>> details.context = getDirective()

          >>> pprint(details.getHandler())
          [('path', 'zope.app.apidoc.zcmlmodule.tests.foo'),
           ('url', 'zope/app/apidoc/zcmlmodule/tests/foo')]
        """
        if self.context.handler is not None:
            path = getPythonPath(self.context.handler)
            return {'path': path,
                    'url': path.replace('.', '/')}
        return None

    def getSubdirectives(self):
        """Create a list of subdirectives.

        Examples::
        
          >>> from zope.app.apidoc.tests import pprint
          >>> from zope.configuration.xmlconfig import ParserInfo
          >>> from zope.interface import Interface
          >>> from zope.publisher.browser import TestRequest
          >>> from tests import getDirective
          >>> details = DirectiveDetails()
          >>> details.context = getDirective()
          >>> details.request = TestRequest()

          >>> class IFoo(Interface):
          ...     pass

          >>> def handler():
          ...     pass

          >>> details.getSubdirectives()
          []

          >>> details.context.subdirs = (
          ...     ('browser', 'foo', IFoo, handler, 'info'),)
          >>> info = details.getSubdirectives()[0]
          >>> info['schema'] = info['schema'].__module__ + '.InterfaceDetails'
          >>> pprint(info)
          [('handler',
            [('path', 'zope.app.apidoc.zcmlmodule.browser.handler'),
             ('url', 'zope/app/apidoc/zcmlmodule/browser/handler')]),
           ('info', 'info'),
           ('name', 'foo'),
           ('namespace', 'browser'),
           ('schema', 'zope.app.apidoc.ifacemodule.browser.InterfaceDetails')]
        """
        dirs = []
        for ns, name, schema, handler, info in self.context.subdirs:
            schema = LocationProxy(schema, self.context, getPythonPath(schema))
            details = InterfaceDetails()
            details.context = schema
            details.request = self.request

            path = getPythonPath(handler)
            dirs.append({'namespace': ns,
                         'name': name,
                         'schema': details,
                         'handler': {'path': path,
                                     'url': path.replace('.', '/')},
                         'info': info})
        return dirs
