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
"""Introspector view for content components


"""
__docformat__ = 'restructuredtext'
import inspect

import zope.interface
import zope.security.proxy
from zope.interface import directlyProvidedBy
from zope.interface import directlyProvides
from zope.location import location
from zope.publisher.browser import BrowserView
from zope.traversing.api import getParent
from zope.traversing.api import traverse
from zope.traversing.interfaces import IContainmentRoot
from zope.traversing.interfaces import IPhysicallyLocatable

from zope import annotation
from zope.app import apidoc


def getTypeLink(type_):
    if isinstance(None, type_):
        return None
    path = apidoc.utilities.getPythonPath(type_)
    importable = apidoc.utilities.isReferencable(path)
    return path.replace('.', '/') if importable else None


class annotationsNamespace:
    """Used to traverse to the annotations of an object."""

    def __init__(self, ob, request=None):
        self.context = ob

    def traverse(self, name, ignore):
        # This is pretty unsafe and one of the reasons why the introspector is
        # only available in dev-mode.
        naked = zope.security.proxy.removeSecurityProxy(self.context)
        annotations = annotation.interfaces.IAnnotations(naked)
        obj = annotations[name] if name else annotations
        if not IPhysicallyLocatable(obj, False):
            obj = location.LocationProxy(
                obj, self.context, '++annotations++' + name)
        return obj


class sequenceItemsNamespace:
    """Used to traverse to the values of a sequence."""

    def __init__(self, ob, request=None):
        self.context = ob

    def traverse(self, name, ignore):
        obj = self.context[int(name)]
        if not IPhysicallyLocatable(obj, False):
            obj = location.LocationProxy(obj, self.context, '++items++' + name)
        return obj


class mappingItemsNamespace:
    """Used to traverse to the values of a mapping.

    Important: This might seem like overkill, but we do not know that (1)
    every mapping has a traverser and (2) whether the location is available. A
    location might not be available, if we have a mapping in the annotations,
    for example.
    """

    def __init__(self, ob, request=None):
        self.context = ob

    def traverse(self, name, ignore):
        obj = self.context[name]
        if not IPhysicallyLocatable(obj, False):
            obj = location.LocationProxy(obj, self.context, '++items++' + name)
        return obj


# Small hack to simulate a traversal root.
@zope.interface.implementer(IContainmentRoot)
class TraversalRoot:
    pass


class Introspector(BrowserView):
    """Introspector browser view"""

    def __init__(self, context, request):
        super().__init__(context, request)
        path = apidoc.utilities.getPythonPath(
            context.__class__).replace('.', '/')

        # the ++apidoc++ namespace overrides the skin, so make sure we can get
        # it back.
        direct = list(directlyProvidedBy(request))

        self.klassView = traverse(
            TraversalRoot(),
            '/++apidoc++/Code/%s/@@index.html' % path, request=request)

        directlyProvides(request, direct)

    def parent(self):
        return getParent(self.context)

    def getBaseURL(self):
        return self.klassView.getBaseURL()

    def getDirectlyProvidedInterfaces(self):
        # Getting the directly provided interfaces works only on naked objects
        obj = zope.security.proxy.removeSecurityProxy(self.context)
        return [apidoc.utilities.getPythonPath(iface)
                for iface in zope.interface.directlyProvidedBy(obj)]

    def getProvidedInterfaces(self):
        return self.klassView.getInterfaces()

    def getBases(self):
        return self.klassView.getBases()

    def getAttributes(self):
        # remove the security proxy, so that `attr` is not proxied. We could
        # unproxy `attr` for each turn, but that would be less efficient.
        #
        # `getPermissionIds()` also expects the class's security checker not
        # to be proxied.
        klass = zope.security.proxy.removeSecurityProxy(self.klassView.context)
        obj = zope.security.proxy.removeSecurityProxy(self.context)

        for name in apidoc.utilities.getPublicAttributes(obj):
            value = getattr(obj, name)
            if inspect.ismethod(value) or inspect.ismethoddescriptor(value):
                # Because getPublicAttributes(obj) loops through
                # dir(obj) which is more or less obj.__dict__, and
                # when obj is an instance (and not a class), its
                # __dict__ tends not to have methods in it, so this condition
                # should typically not be taken.
                continue  # pragma: no cover
            entry = {
                'name': name,
                'value': repr(value),
                'value_linkable': IPhysicallyLocatable(value, False) and True,
                'type': type(value).__name__,
                'type_link': getTypeLink(type(value)),
                'interface': apidoc.utilities.getInterfaceForAttribute(
                    name, klass._Class__all_ifaces)
            }
            entry.update(apidoc.utilities.getPermissionIds(
                name, klass.getSecurityChecker()))
            yield entry

    def getMethods(self):
        # remove the security proxy, so that `attr` is not proxied. We could
        # unproxy `attr` for each turn, but that would be less efficient.
        #
        # `getPermissionIds()` also expects the class's security checker not
        # to be proxied.
        klass = zope.security.proxy.removeSecurityProxy(self.klassView.context)
        obj = zope.security.proxy.removeSecurityProxy(self.context)

        for name in apidoc.utilities.getPublicAttributes(obj):
            val = getattr(obj, name)
            if not (inspect.ismethod(val) or inspect.ismethoddescriptor(val)):
                continue

            signature = apidoc.utilities.getFunctionSignature(val)

            entry = {
                'name': name,
                'signature': signature,
                'doc': apidoc.utilities.renderText(
                    val.__doc__ or '',
                    getParent(self.klassView.context).getPath()),
                'interface': apidoc.utilities.getInterfaceForAttribute(
                    name, klass._Class__all_ifaces)}

            entry.update(apidoc.utilities.getPermissionIds(
                name, klass.getSecurityChecker()))

            yield entry

    def isSequence(self):
        return zope.interface.common.sequence.IExtendedReadSequence.providedBy(
            self.context)

    def getSequenceItems(self):
        ann = []
        # Make the object naked, so that we can inspect the value types.
        naked = zope.security.proxy.removeSecurityProxy(self.context)
        for index in range(0, len(self.context)):
            value = naked[index]
            ann.append({
                'index': index,
                'value': repr(value),
                'value_type': type(value).__name__,
                'value_type_link': getTypeLink(type(value))
            })
        return ann

    def isMapping(self):
        return zope.interface.common.mapping.IEnumerableMapping.providedBy(
            self.context)

    def getMappingItems(self):
        ann = []
        # Make the object naked, so that we can inspect the value types.
        naked = zope.security.proxy.removeSecurityProxy(self.context)
        for key, value in naked.items():
            ann.append({
                'key': key,
                'key_string': repr(key),
                'value': repr(value),
                'value_type': type(value).__name__,
                'value_type_link': getTypeLink(type(value))
            })
        return ann

    def isAnnotatable(self):
        return annotation.interfaces.IAnnotatable.providedBy(self.context)

    def getAnnotationsInfo(self):
        # We purposefully strip the security here; this is the introspector,
        # so we want to see things that we usually cannot see
        naked = zope.security.proxy.removeSecurityProxy(self.context)
        annotations = annotation.interfaces.IAnnotations(naked)
        ann = []
        for key, value in annotations.items():
            ann.append({
                'key': key,
                'key_string': repr(key),
                'value': repr(value),
                'value_type': type(value).__name__,
                'value_type_link': getTypeLink(type(value))
            })
        return ann
