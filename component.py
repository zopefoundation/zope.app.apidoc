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
"""Component Inspection Utilities

$Id$
"""
__docformat__ = 'restructuredtext'
import types

from zope.component.interfaces import IFactory
from zope.component.site import AdapterRegistration, SubscriptionRegistration
from zope.component.site import UtilityRegistration
from zope.interface import Interface
from zope.interface.interface import InterfaceClass
from zope.publisher.interfaces import IRequest

from zope.app import zapi
from zope.app.i18n import ZopeMessageFactory as _
from zope.app.apidoc.classregistry import classRegistry
from zope.app.apidoc.utilities import relativizePath, truncateSysPath
from zope.app.apidoc.utilities import getPythonPath, isReferencable, renderText
from zope.app.apidoc.utilitymodule import utilitymodule

SPECIFIC_INTERFACE_LEVEL = 1
EXTENDED_INTERFACE_LEVEL = 2
GENERIC_INTERFACE_LEVEL = 4

def getRequiredAdapters(iface, withViews=False):
    """Get adapter registrations where the specified interface is required."""
    gsm = zapi.getGlobalSiteManager()
    for reg in gsm.registrations():
        # Only get adapters
        if not isinstance(reg, (AdapterRegistration, SubscriptionRegistration)):
            continue
        # Ignore adapters that have no required interfaces
        if len(reg.required) == 0:
            continue
        # Ignore views
        if not withViews and reg.required[-1] and \
               reg.required[-1].isOrExtends(IRequest):
            continue
        # Only get the adapters for which this interface is required
        for required_iface in reg.required:
            if iface.isOrExtends(required_iface):
                yield reg


def getProvidedAdapters(iface, withViews=False):
    """Get adapter registrations where this interface is provided."""
    gsm = zapi.getGlobalSiteManager()
    for reg in gsm.registrations():
        # Only get adapters
        if not isinstance(reg, (AdapterRegistration, SubscriptionRegistration)):
            continue
        # Ignore adapters that have no required interfaces
        if len(reg.required) == 0:
            continue
        # Ignore views
        if not withViews and reg.required[-1] and \
               reg.required[-1].isOrExtends(IRequest):
            continue
        # Only get adapters for which this interface is provided
        if reg.provided is None or not reg.provided.isOrExtends(iface):
            continue
        yield reg


def filterAdapterRegistrations(regs, iface, level=SPECIFIC_INTERFACE_LEVEL):
    """Return only those registrations that match the specifed level"""
    for reg in regs:
        if level & GENERIC_INTERFACE_LEVEL:
            for required_iface in reg.required:
                if required_iface in (Interface, None):
                    yield reg
                    continue

        if level & EXTENDED_INTERFACE_LEVEL:
            for required_iface in reg.required:
                if required_iface is not Interface and \
                       iface.extends(required_iface):
                    yield reg
                    continue

        if level & SPECIFIC_INTERFACE_LEVEL:
            for required_iface in reg.required:
                if required_iface is iface:
                    yield reg
                    continue


def getClasses(iface):
    """Get the classes that implement this interface."""
    return classRegistry.getClassesThatImplement(iface)


def getFactories(iface):
    """Return the factory registrations, who will return objects providing this
    interface."""
    gsm = zapi.getGlobalSiteManager()
    for reg in gsm.registrations():
        if not isinstance(reg, UtilityRegistration):
            continue
        if reg.provided is not IFactory:
            continue
        interfaces = reg.component.getInterfaces()
        try:
            if interfaces.isOrExtends(iface):
                yield reg
        except AttributeError:
            for interface in interfaces:
                if interface.isOrExtends(iface):
                    yield reg
                    break


def getUtilities(iface):
    """Return all utility registrations that provide the interface."""
    gsm = zapi.getGlobalSiteManager()
    for reg in gsm.registrations():
        if not isinstance(reg, UtilityRegistration):
            continue
        if reg.provided.isOrExtends(iface):
            yield reg


def getRealFactory(factory):
    """Get the real factory.

    Sometimes the original factory is masked by functions. If the function
    keeps track of the original factory, use it.
    """
    if isinstance(factory, types.FunctionType) and hasattr(factory, 'factory'):
        return factory.factory
    elif not hasattr(factory, '__name__'):
        # We have an instance
        return factory.__class__
    return factory


def getParserInfoInfoDictionary(info):
    """Return a PT-friendly info dictionary for a parser info object."""
    return {'file': relativizePath(info.file),
            'url': truncateSysPath(info.file).replace('\\', '/'),
            'line': info.line,
            'eline': info.eline,
            'column': info.column,
            'ecolumn': info.ecolumn}


def getInterfaceInfoDictionary(iface):
    """Return a PT-friendly info dictionary for an interface."""
    if iface is None:
        return None
    return {'module': iface.__module__, 'name': iface.getName()}


def getAdapterInfoDictionary(reg):
    """Return a PT-friendly info dictionary for an adapter registration."""
    factory = getRealFactory(reg.value)
    path = getPythonPath(factory)

    url = None
    if isReferencable(path):
        url = path.replace('.', '/')

    if isinstance(reg.doc, (str, unicode)):
        doc = reg.doc
        zcml = None
    else:
        doc = None
        zcml = getParserInfoInfoDictionary(reg.doc)

    return {
        'provided': getInterfaceInfoDictionary(reg.provided),
        'required': [getInterfaceInfoDictionary(iface)
                     for iface in reg.required
                     if iface is not None],
        'name': getattr(reg, 'name', _('<subscription>')),
        'factory': path,
        'factory_url': url,
        'doc': doc,
        'zcml': zcml}


def getFactoryInfoDictionary(reg):
    """Return a PT-friendly info dictionary for a factory."""
    factory = reg.component
    callable = factory

    # Usually only zope.component.factory.Factory instances have this attribute
    if IFactory.providedBy(factory) and hasattr(factory, '_callable'):
        callable = factory._callable
    elif hasattr(callable, '__class__'):
        callable = callable.__class__

    path = getPythonPath(callable)

    return {'name': reg.name or _('<i>no name</i>'),
            'title': getattr(factory, 'title', u''),
            'description': renderText(getattr(factory, 'description', u''),
                                      module=callable.__module__),
            'url': isReferencable(path) and path.replace('.', '/') or None}


def getUtilityInfoDictionary(reg):
    """Return a PT-friendly info dictionary for a factory."""
    component = reg.component
    # Check whether we have an instance of some custom type or not
    # Unfortunately, a lot of utilities have a `__name__` attribute, so we
    # cannot simply check for its absence
    # TODO: Once we support passive display of instances, this insanity can go
    #       away.
    if not isinstance(component, (types.MethodType, types.FunctionType,
                                  types.ClassType, types.TypeType,
                                  InterfaceClass)):
        component = getattr(component, '__class__', component)

    path = getPythonPath(component)

    # provided interface id
    iface_id = '%s.%s' % (reg.provided.__module__, reg.provided.getName())

    # Determine the URL
    if isinstance(component, InterfaceClass):
        url = 'Interface/%s' %path
    else:
        url = None
        if isReferencable(path):
            url = 'Code/%s' % path.replace('.', '/')

    return {'name': reg.name or _('<i>no name</i>'),
            'url_name': utilitymodule.encodeName(reg.name or '__noname__'),
            'iface_id': iface_id,
            'path': path,
            'url': url}
