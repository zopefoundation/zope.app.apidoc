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
"""Browser Views for ZCML Reference

$Id: browser.py,v 1.1 2004/02/19 20:46:43 philikon Exp $
"""
import urllib

from zope.proxy import removeAllProxies
from zope.schema import getFieldsInOrder 
from zope.configuration.xmlconfig import ParserInfo

from zope.app import zapi
from zope.app.location import LocationProxy
from zope.app.apidoc.zcmlmodule import Directive, Namespace
from zope.app.apidoc.ifacemodule.browser import InterfaceDetails
from zope.app.apidoc.utilities import getPythonPath

__metaclass__ = type

class Menu:
    """Menu View Helper Class"""

    def getMenuTitle(self, node):
        """Return the title of the node that is displayed in the menu."""
        obj = removeAllProxies(node.context)
        if isinstance(obj, Namespace):
            name = obj.getShortName()
            if name == 'ALL':
                return 'All Namespaces'
            return name
        return zapi.name(obj)

    def getMenuLink(self, node):
        """Return the HTML link of the node that is displayed in the menu."""
        obj = removeAllProxies(node.context)
        if isinstance(obj, Directive):
            ns = zapi.getParent(obj)
            return './'+zapi.name(ns) + '/' + zapi.name(obj) + '/index.html'
        return None

class DirectiveDetails:
    """View class for a Directive."""

    def getSchema(self):
        """Return the schema of the directive.""" 
        schema = LocationProxy(self.context.schema,
                               self.context,
                               getPythonPath(self.context.schema))
        return InterfaceDetails(schema, self.request)

    def getNamespaceName(self):
        """Return the name of the namespace."""
        name = zapi.getParent(self.context).getFullName()
        if name == 'ALL':
            return '<i>all namespaces</i>'
        return name

    def getFile(self):
        """Get the file where the directive was declared."""
        info = removeAllProxies(self.context.info)
        if isinstance(info, ParserInfo):
            return info.file
        return None

    def getInfo(self):
        """Get info, if available."""
        info = removeAllProxies(self.context.info)
        if isinstance(info, ParserInfo):
            return None
        return info
    
    def getSubdirectives(self):
        """Create a list of subdirectives."""
        dirs = []
        for ns, name, schema, info in self.context.subdirs:
            schema = LocationProxy(schema, self.context, getPythonPath(schema))
            schema = InterfaceDetails(schema, self.request)
            dirs.append({'namespace': ns,
                         'name': name,
                         'schema': schema,
                         'info': info})
        return dirs
