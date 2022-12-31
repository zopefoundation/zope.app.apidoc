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
"""Browser Views for ZCML Reference

"""
__docformat__ = 'restructuredtext'
import keyword

from zope.configuration.xmlconfig import ParserInfo
from zope.location import LocationProxy
from zope.security.proxy import isinstance
from zope.security.proxy import removeSecurityProxy
from zope.traversing.api import getName
from zope.traversing.api import getParent

from zope.app.apidoc.browser.utilities import findAPIDocumentationRootURL
from zope.app.apidoc.ifacemodule.browser import InterfaceDetails
from zope.app.apidoc.utilities import getPythonPath
from zope.app.apidoc.utilities import isReferencable
from zope.app.apidoc.utilities import relativizePath
from zope.app.apidoc.zcmlmodule import Directive
from zope.app.apidoc.zcmlmodule import Namespace


class Menu:
    """Menu View Helper Class"""
    context = None
    request = None

    def getMenuTitle(self, node):
        """Return the title of the node that is displayed in the menu."""
        obj = node.context
        if isinstance(obj, Namespace):
            name = obj.getShortName()
            if name == 'ALL':
                return 'All Namespaces'
            return name
        return getName(obj)

    def getMenuLink(self, node):
        """Return the HTML link of the node that is displayed in the menu."""
        obj = node.context
        if isinstance(obj, Directive):
            ns = getParent(obj)
            apidoc_url = findAPIDocumentationRootURL(
                self.context, self.request)
            return '{}/ZCML/{}/{}/index.html'.format(
                apidoc_url, getName(ns), getName(obj))
        return None


def _getFieldName(field):
    name = field.getName()
    if name.endswith("_") and keyword.iskeyword(name[:-1]):
        name = name[:-1]
    return name


class DirectiveDetails:
    """View class for a Directive."""

    context = None
    request = None

    def getAPIDocRootURL(self):
        return findAPIDocumentationRootURL(self.context, self.request)

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
        name = getParent(self.context).getFullName()
        if name == 'ALL':
            return '<i>all namespaces</i>'
        return name

    def getFileInfo(self):
        """Get the file where the directive was declared."""
        # ZCML directive `info` objects do not have security declarations, so
        # everything is forbidden by default. We need to remove the security
        # proxies in order to get to the data.
        info = removeSecurityProxy(self.context.info)
        if isinstance(info, ParserInfo):
            return {'file': relativizePath(info.file),
                    'line': info.line,
                    'column': info.column,
                    'eline': info.eline,
                    'ecolumn': info.ecolumn}

    def getInfo(self):
        """Get the file where the directive was declared."""
        if isinstance(self.context.info, str):
            return self.context.info
        return None

    def getHandler(self):
        """Return information about the handler."""
        if self.context.handler is not None:
            path = getPythonPath(self.context.handler)
            return {
                'path': path,
                'url': isReferencable(path) and path.replace('.', '/') or None}

    def getSubdirectives(self):
        """Create a list of subdirectives."""
        dirs = []
        for ns, name, schema, handler, info in self.context.subdirs:
            details = self._getInterfaceDetails(schema)
            path = getPythonPath(handler)
            url = path.replace('.', '/') if isReferencable(path) else None
            dirs.append({
                'namespace': ns,
                'name': name,
                'schema': details,
                'handler': {'path': path, 'url': url},
                'info': info,
            })
        return dirs
