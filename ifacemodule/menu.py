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
"""Interface Module Browser Menu (Tree)

A list of interfaces from the Interface Service is pretty much unmanagable and
is very confusing. Therefore it is nice to split the path of the interface, so
that we get a deeper tree with nodes having shorter, manageable names.

$Id$
"""
__docformat__ = 'restructuredtext'

from zope.interface import implements
from zope.security.proxy import removeSecurityProxy

from zope.app import zapi
from zope.app.location.interfaces import ILocation
from zope.app.location import LocationProxy
from zope.app.tree.interfaces import IChildObjects

from zope.app.apidoc.ifacemodule import IInterfaceModule
from zope.app.apidoc.utilities import ReadContainerBase

class IModule(ILocation):
    """Represents some module

    Marker interface, so that we can register an adapter for it."""
    

class Module(ReadContainerBase):
    r"""Represents a Python module

    Examples: zope, zope.app, zope.app.interfaces

    However, we usually use it only for the last case.

    Usage::

      >>> from zope.app.apidoc.ifacemodule import InterfaceModule

      >>> module = Module(InterfaceModule(), 'zope.app')
      >>> module.get('apidoc.interfaces.IDocumentationModule').getName()
      'IDocumentationModule'

      >>> module.get(
      ...     'zope.app.apidoc.interfaces.IDocumentationModule') is None
      True

      >>> print '\n'.join([id for id, iface in module.items()])
      zope.app.apidoc.interfaces.IDocumentationModule
    """
    
    implements(IModule)

    def __init__(self, parent, name):
        self.__parent__ = parent
        self.__name__ = name

    def get(self, key, default=None):
        name = self.__name__ + '.' + key
        return self.__parent__.get(name, default)

    def items(self):
        parent = self.__parent__
        items = []
        for key in parent.keys():
            if key.startswith(self.__name__):
                items.append((key, LocationProxy(parent[key], self, key)))
        return items


class InterfaceModuleChildObjects(object):
    r"""Module Adapter for Static Tree

    This adapter is used when building a static tree for the browser.

    Functionality::

      >>> from zope.app.apidoc.ifacemodule import InterfaceModule
      >>> from zope.app.apidoc.ifacemodule import tests

      >>> module = InterfaceModule()
      >>> module = tests.rootLocation(module, 'Interface')
      >>> adapter = InterfaceModuleChildObjects(module)
      >>> adapter.hasChildren()
      True

      >>> print '\n'.join([c.__name__ for c in adapter.getChildObjects()])
      IInterfaceModule
      zope.app.apidoc.interfaces
    """

    implements(IChildObjects)
    __used_for__ = IInterfaceModule

    def __init__(self, context):
        self.context = context

    def hasChildren(self):
        """See zope.app.tree.interfaces.IChildObject"""
        return bool(len(self.context))

    def getChildObjects(self):
        """See zope.app.tree.interfaces.IChildObject"""
        objects = {}
        names = removeSecurityProxy(self.context.keys())
        names.sort()
        for name in names:
            # Split these long names and make part of the module path separate
            # entries. Currently we only split by the term '.interfaces', but
            # a more sophisticated algorithm could be developed. 
            iface_loc = name.find('.interfaces')
            if iface_loc == -1:
                objects[name] = LocationProxy(self.context[name],
                                              self.context, name)
            else:
                module_name = name[:iface_loc+11]
                objects[module_name] = Module(self.context, module_name)
        items = objects.items()
        items.sort()
        return [x[1] for x in items]


class Menu(object):
    """Menu View Helper Class

    A class that helps building the menu. The menu_macros expects the menu view
    class to have the `getMenuTitle(node)` and `getMenuLink(node)` methods
    implemented. ``node`` is a ``zope.app.tree.node.Node`` instance.

    Examples::

      >>> from zope.app.apidoc.ifacemodule import InterfaceModule
      >>> from zope.app.apidoc.ifacemodule.tests import Root
      >>> from zope.app.tree.node import Node 

      >>> ifacemod = InterfaceModule()
      >>> ifacemod.__parent__ = Root()
      >>> ifacemod.__name__ = 'Interfaces'
      >>> mod = Module(ifacemod, 'zope.app.apidoc.interfaces')
      >>> menu = Menu()

      >>> node = Node(mod.get('IDocumentationModule'))
      >>> menu.getMenuTitle(node)
      'zope.app.apidoc.interfaces.IDocumentationModule'

      >>> values = mod.values()
      >>> values.sort()
      >>> node = Node(values[0])
      >>> menu.getMenuTitle(node)
      u'IDocumentationModule'

      >>> menu.getMenuLink(node)
      u'./zope.app.apidoc.interfaces.IDocumentationModule/apiindex.html'
    """

    def getMenuTitle(self, node):
        """Return the title of the node that is displayed in the menu."""
        if zapi.isinstance(node.context.__parent__, Module):
            parent = node.context.__parent__
            return zapi.name(node.context).replace(zapi.name(parent)+'.', '')
        return zapi.name(node.context)

    def getMenuLink(self, node):
        """Return the HTML link of the node that is displayed in the menu."""
        if zapi.isinstance(node.context, Module):
            return None
        return './' + zapi.name(node.context) + '/apiindex.html'
