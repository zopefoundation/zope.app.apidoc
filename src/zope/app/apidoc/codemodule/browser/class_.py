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
"""Class Views

"""
__docformat__ = 'restructuredtext'

import inspect

from zope.proxy import removeAllProxies
from zope.security.proxy import removeSecurityProxy
from zope.traversing.api import getParent
from zope.traversing.api import traverse
from zope.traversing.browser import absoluteURL
from zope.traversing.interfaces import TraversalError

from zope.app.apidoc.browser.utilities import findAPIDocumentationRoot
from zope.app.apidoc.utilities import getFunctionSignature
from zope.app.apidoc.utilities import getPermissionIds
from zope.app.apidoc.utilities import getPythonPath
from zope.app.apidoc.utilities import isReferencable
from zope.app.apidoc.utilities import renderText


def getTypeLink(type, _NoneType=type(None)):
    if type is _NoneType:
        return None
    path = getPythonPath(type)
    return path.replace('.', '/') if isReferencable(path) else None


def getInterfaceInfo(iface):
    if iface is None:
        return None
    path = getPythonPath(iface)
    return {'path': path,
            'url': isReferencable(path) and path or None}


class ClassDetails:
    """Represents the details of the class."""

    context = None
    request = None

    def getBases(self):
        """Get all bases of this class."""
        return self._listClasses(self.context.getBases())

    def getKnownSubclasses(self):
        """Get all known subclasses of this class."""
        entries = self._listClasses(self.context.getKnownSubclasses())
        entries.sort(key=lambda x: x['path'])
        return entries

    def _getCodeModule(self):
        apidoc = findAPIDocumentationRoot(self.context)
        return apidoc['Code']

    def _listClasses(self, classes):
        """Prepare a list of classes for presentation."""
        info = []
        codeModule = self._getCodeModule()
        for cls in classes:
            # We need to removeAllProxies because the security checkers for
            # zope.container.contained.ContainedProxy and
            # zope.app.i18n.messagecatalog.MessageCatalog prevent us from
            # accessing __name__ and __module__.
            unwrapped_cls = removeAllProxies(cls)
            path = getPythonPath(unwrapped_cls)
            url = None
            try:
                klass = traverse(codeModule, path.replace('.', '/'))
                url = absoluteURL(klass, self.request)
            except TraversalError:
                # If one of the classes is implemented in C, we will not
                # be able to find it.
                # Likewise, if we are attempting to get a root module that
                # was not a registered root, the CodeModule will not be able to
                # find it either.
                pass
            info.append({'path': path or None, 'url': url})
        return info

    def getBaseURL(self):
        """Return the URL for the API Documentation Tool."""
        m = self._getCodeModule()
        return absoluteURL(getParent(m), self.request)

    def getInterfaces(self):
        """Get all implemented interfaces (as paths) of this class."""
        return [getInterfaceInfo(iface)
                for iface in self.context.getInterfaces()]

    def getAttributes(self):
        """Get all attributes of this class."""
        attrs = []
        # remove the security proxy, so that `attr` is not proxied. We could
        # unproxy `attr` for each turn, but that would be less efficient.
        #
        # `getPermissionIds()` also expects the class's security checker not
        # to be proxied.
        klass = removeSecurityProxy(self.context)
        for name, attr, iface in klass.getAttributes():
            entry = {'name': name,
                     'value': repr(attr),
                     'type': type(attr).__name__,
                     'type_link': getTypeLink(type(attr)),
                     'interface': getInterfaceInfo(iface)}
            entry.update(getPermissionIds(name, klass.getSecurityChecker()))
            attrs.append(entry)
        return attrs

    def getMethods(self):
        """Get all methods of this class."""
        methods = []
        # remove the security proxy, so that `attr` is not proxied. We could
        # unproxy `attr` for each turn, but that would be less efficient.
        #
        # `getPermissionIds()` also expects the class's security checker not
        # to be proxied.
        klass = removeSecurityProxy(self.context)
        for name, attr, iface in klass.getMethodDescriptors():
            entry = {'name': name,
                     'signature': "(...)",
                     'doc': renderText(attr.__doc__ or '',
                                       inspect.getmodule(attr)),
                     'interface': getInterfaceInfo(iface)}
            entry.update(getPermissionIds(name, klass.getSecurityChecker()))
            methods.append(entry)

        for name, attr, iface in klass.getMethods():
            entry = {'name': name,
                     'signature': getFunctionSignature(attr, ignore_self=True),
                     'doc': renderText(attr.__doc__ or '',
                                       inspect.getmodule(attr)),
                     'interface': getInterfaceInfo(iface)}
            entry.update(getPermissionIds(name, klass.getSecurityChecker()))
            methods.append(entry)
        return methods

    def getDoc(self):
        """Get the doc string of the class STX formatted."""
        return renderText(self.context.getDocString() or '',
                          getParent(self.context).getPath())

    def getConstructor(self):
        """Get info about the constructor, or None if there isn't one."""
        attr = self.context.getConstructor()
        if attr is not None:
            attr = removeSecurityProxy(attr)
            return {
                'signature': getFunctionSignature(attr, ignore_self=True),
                'doc': renderText(attr.__doc__ or '', inspect.getmodule(attr)),
            }
