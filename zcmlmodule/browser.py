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

import keyword

from zope.configuration.xmlconfig import ParserInfo
from zope.security.proxy import removeSecurityProxy

from zope.app import zapi
from zope.app.location import LocationProxy
from zope.app.apidoc.zcmlmodule import Directive, Namespace
from zope.app.apidoc.ifacemodule.browser import InterfaceDetails
from zope.app.apidoc.utilities import getPythonPath, relativizePath

class Menu(object):
    """Menu View Helper Class"""

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


def _getFieldName(field):
    name = field.getName()
    if name.endswith("_") and keyword.iskeyword(name[:-1]):
        name = name[:-1]
    return name


class DirectiveDetails(object):
    """View class for a Directive."""

    def _getInterfaceDetails(self, schema):
        schema = LocationProxy(schema,
                               self.context,
                               getPythonPath(schema))
        details = InterfaceDetails(schema, self.request)
        details._getFieldName = _getFieldName
        return details

    def getSchema(self):
        """Return the schema of the directive."""
        return self._getInterfaceDetails(self.context.schema)

    def getNamespaceName(self):
        """Return the name of the namespace."""
        name = zapi.getParent(self.context).getFullName()
        if name == 'ALL':
            return '<i>all namespaces</i>'
        return name

    def getFileInfo(self):
        """Get the file where the directive was declared."""
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
        """Get the file where the directive was declared."""
        if isinstance(self.context.info, (str, unicode)):
            return self.context.info
        return None

    def getHandler(self):
        """Return information about the handler."""
        if self.context.handler is not None:
            path = getPythonPath(self.context.handler)
            return {'path': path,
                    'url': path.replace('.', '/')}
        return None

    def getSubdirectives(self):
        """Create a list of subdirectives."""
        dirs = []
        for ns, name, schema, handler, info in self.context.subdirs:
            details = self._getInterfaceDetails(schema)
            path = getPythonPath(handler)
            dirs.append({
                'namespace': ns,
                'name': name,
                'schema': details,
                'handler': {'path': path,
                            'url': path.replace('.', '/')},
                'info': info,
                })
        return dirs
