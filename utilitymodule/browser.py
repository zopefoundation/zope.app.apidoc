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
"""Utility Module Views

$Id: browser.py,v 1.1 2004/02/19 20:46:42 philikon Exp $
"""
from zope.app import zapi
from zope.app.location import LocationProxy
from zope.app.apidoc.ifacemodule.browser import InterfaceDetails
from zope.app.apidoc.utilities import getPythonPath
from zope.app.apidoc.utilitymodule import NONAME, Utility, UtilityInterface
from zope.proxy import removeAllProxies

__metaclass__ = type

class UtilityDetails:
    """Utility Details View."""

    def getName(self):
        """Get the name of the utility.

        Return the string "no name", if the utility has no name.
        """
        name = zapi.name(self.context)
        if name == NONAME:
            return 'no name'
        return name

    def getInterface(self):
        """Return the interface the utility provides.""" 
        schema = LocationProxy(self.context.interface,
                               self.context,
                               getPythonPath(self.context.interface))
        return InterfaceDetails(schema, self.request)

    def getComponent(self):
        """Return the python path of the implementation class."""
        if isinstance(self.context.component, (unicode, str)):
            return None #self.context.component
        return getPythonPath(self.context.component.__class__)

class Menu:
    """Menu View Helper Class

    A class that helps building the menu. The menu_macros expects the menu view
    class to have the getMenuTitle(node) and getMenuLink(node) methods
    implemented. 'node' is a 'zope.app.tree.node.Node' instance.
    """

    def getMenuTitle(self, node):
        """Return the title of the node that is displayed in the menu."""
        obj = removeAllProxies(node.context)
        if zapi.name(obj) == NONAME:
            return 'no name'
        if isinstance(obj, UtilityInterface):
            return zapi.name(obj).split('.')[-1]
        return zapi.name(obj)

    def getMenuLink(self, node):
        """Return the HTML link of the node that is displayed in the menu."""
        obj = removeAllProxies(node.context)
        if isinstance(obj, Utility):
            iface = zapi.getParent(obj)
            return './'+zapi.name(iface) + '/' + zapi.name(obj) + '/index.html'
        if isinstance(obj, UtilityInterface):
            return '../Interface/'+zapi.name(obj) + '/apiindex.html'
        return None
