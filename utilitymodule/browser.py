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
"""Utility Module Views

$Id$
"""
__docformat__ = 'restructuredtext'

from types import InstanceType
from zope.app import zapi
from zope.app.location import LocationProxy
from zope.app.apidoc.ifacemodule.browser import InterfaceDetails
from zope.app.apidoc.utilities import getPythonPath
from zope.app.apidoc.utilitymodule import NONAME, Utility, UtilityInterface

class UtilityDetails(object):
    """Utility Details View."""

    def getName(self):
        """Get the name of the utility.

        Return the string ``no name``, if the utility has no name.

        Examples::

          >>> def makeRegistration(name):
          ...     return type('RegistrationStub', (),
          ...                 {'name': name, 'provided': None,
          ...                  'component': None, 'doc': ''})()

          >>> details = UtilityDetails()
          >>> details.context = Utility(None, makeRegistration('myname'))
          >>> details.getName()
          'myname'

          >>> details.context = Utility(None, makeRegistration(NONAME))
          >>> details.getName()
          'no name'
        """
        name = zapi.name(self.context)
        if name == NONAME:
            return 'no name'
        return name

    def getInterface(self):
        """Return the interface the utility provides.

        Example::

          >>> from tests import getDetailsView
          >>> details = getDetailsView()

          >>> iface = details.getInterface()
          >>> iface.getId()
          'zope.app.apidoc.interfaces.IDocumentationModule'
        """ 
        schema = LocationProxy(self.context.interface,
                               self.context,
                               getPythonPath(self.context.interface))
        details = InterfaceDetails()
        details.context = schema
        details.request = self.request
        
        return details

    def getComponent(self):
        """Return the python path of the implementation class.

        Examples::

          >>> from zope.app.apidoc.utilitymodule import Utility
          >>> from zope.app.apidoc.tests import pprint

          >>> def makeRegistration(name, component):
          ...     return type(
          ...         'RegistrationStub', (),
          ...         {'name': name, 'provided': None,
          ...          'component': component, 'doc': ''})()

          >>> class Foo(object):
          ...     pass

          >>> class Bar(object):
          ...     pass

          >>> details = UtilityDetails()
          >>> details.context = Utility(None, makeRegistration('', Foo()))
          >>> pprint(details.getComponent())
          [('path', 'zope.app.apidoc.utilitymodule.browser.Foo'),
           ('url', 'zope/app/apidoc/utilitymodule/browser/Foo')]

          >>> details.context = Utility(None, makeRegistration('', Bar()))
          >>> pprint(details.getComponent())
          [('path', 'zope.app.apidoc.utilitymodule.browser.Bar'),
           ('url', 'zope/app/apidoc/utilitymodule/browser/Bar')]
        """
        # We could use `type()` here, but then we would need to remove the
        # security proxy from the component. This is easier and also supports
        # old-style classes 
        klass = self.context.component.__class__

        return {'path': getPythonPath(klass),
                'url':  getPythonPath(klass).replace('.', '/')}

class Menu(object):
    """Menu View Helper Class

    A class that helps building the menu. The menu_macros expects the menu view
    class to have the `getMenuTitle(node)` and `getMenuLink(node)` methods
    implemented. `node` is a `zope.app.tree.node.Node` instance.

    Examples::

      >>> from zope.app.tree.node import Node 
      >>> from zope.app.apidoc.utilitymodule import Utility, UtilityInterface
      >>> from zope.app.apidoc.tests import Root
      >>> menu = Menu()

      >>> def makeRegistration(name):
      ...     return type('RegistrationStub', (),
      ...                 {'name': name, 'provided': None,
      ...                  'component': None, 'doc': ''})()

      Get menu title and link for a utility interface

      >>> uiface = UtilityInterface(Root(), 'foo.bar.iface', None)
      >>> node = Node(uiface)
      >>> menu.getMenuTitle(node)
      'iface'
      >>> menu.getMenuLink(node)
      '../Interface/foo.bar.iface/apiindex.html'

      Get menu title and link for a utility with a name

      >>> util = Utility(uiface, makeRegistration('FooBar'))
      >>> node = Node(util)
      >>> menu.getMenuTitle(node)
      'FooBar'
      >>> menu.getMenuLink(node)
      './foo.bar.iface/FooBar/index.html'

      Get menu title and link for a utility without a name

      >>> util = Utility(uiface, makeRegistration(None))
      >>> node = Node(util)
      >>> menu.getMenuTitle(node)
      'no name'
      >>> menu.getMenuLink(node)
      './foo.bar.iface/__noname__/index.html'
    """

    def getMenuTitle(self, node):
        """Return the title of the node that is displayed in the menu."""
        obj = node.context
        if zapi.name(obj) == NONAME:
            return 'no name'
        if zapi.isinstance(obj, UtilityInterface):
            return zapi.name(obj).split('.')[-1]
        return zapi.name(obj)

    def getMenuLink(self, node):
        """Return the HTML link of the node that is displayed in the menu."""
        obj = node.context
        if zapi.isinstance(obj, Utility):
            iface = zapi.getParent(obj)
            return './'+zapi.name(iface) + '/' + zapi.name(obj) + '/index.html'
        if zapi.isinstance(obj, UtilityInterface):
            return '../Interface/'+zapi.name(obj) + '/apiindex.html'
        return None
