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
"""Interface Details View

$Id: browser.py,v 1.1 2004/02/19 20:46:41 philikon Exp $
"""

from zope.component import ComponentLookupError
from zope.interface.declarations import providedBy, directlyProvidedBy
from zope.interface.interfaces import IMethod, IAttribute, IInterface 
from zope.proxy import removeAllProxies
from zope.schema.interfaces import IField

from zope.app import zapi
from zope.app.apidoc.utilities import getPythonPath, stx2html

def _get(iface, type):
    """Return a dictionary containing all the Fields in a schema."""
    iface = removeAllProxies(iface)
    items = {}
    for name in iface:
        attr = iface[name]
        if type.isImplementedBy(attr):
            items[name] = attr
    return items

def _getInOrder(iface, type,
                _itemsorter=lambda x, y: cmp(x[1].order, y[1].order)):
    """Return a list of (name, value) tuples in native schema order."""
    items = _get(iface, type).items()
    items.sort(_itemsorter)
    return items

def _getFieldInterface(field):
    """Return PT-friendly dict about the field's interface."""
    field = removeAllProxies(field)
    # This is bad, but due to bootstrapping, directlyProvidedBy does
    # not work 
    name = field.__class__.__name__
    ifaces = list(providedBy(field))
    for iface in ifaces:
        if iface.getName() == 'I' + name:
            return {'name': iface.getName(), 'id': getPythonPath(iface)}
    # Giving up...
    return {'name': ifaces[0].getName(), 'id': getPythonPath(ifaces[0])}

def _getRequired(field):
    """Return a string representation of whether the field is required."""
    if field.required:
        return 'required'
    else:
        return 'optional'


class InterfaceDetails(object):
    """View class for an Interface."""

    def __init__(self, context, request):
        self.context = context
        self.request = request

    def getId(self):
        """Return the id of the field as it is defined in the interface
        service."""
        return zapi.name(self.context)

    def getDoc(self):
        """Return the main documentation string of the interface."""
        return stx2html(self.context.getDoc())

    def getBases(self):
        """Get all bases of this class"""
        return [getPythonPath(base) for base in self.context.__bases__]

    def getTypes(self):
        """Return a list of interface types that are specified for this
        interface.

        Note that you should only expect one type at a time."""
        context = removeAllProxies(self.context)
        types = list(providedBy(context))
        types.remove(IInterface)
        return [{'name': type.getName(),
                 'path': getPythonPath(type)}
                for type in types]
    
    def getAttributes(self):
        """Return a list of attributes in the order they were specified."""
        iface = removeAllProxies(self.context)
        attrs = []
        for name in iface:
            attr = iface[name]
            if not IMethod.isImplementedBy(attr) and \
               not IField.isImplementedBy(attr):
                attrs.append(attr)
        return [{'name': attr.getName(),
                 'doc': stx2html(attr.getDoc() or '', 3)}
                for attr in attrs]

    def getMethods(self):
        """Return a list of methods in the order they were specified."""
        methods = []
        return [{'name': method.getName(),
                 'signature': method.getSignatureString(),
                 'doc': stx2html(method.getDoc() or '', 3)}
                for method in _get(self.context, IMethod).values()]
            
    def getFields(self):
        """Return a list of fields in the order they were specified."""
        fields = map(lambda x: x[1], _getInOrder(self.context, IField))
        return [{'name': field.getName(),
                 'iface': _getFieldInterface(field),
                 'required': _getRequired(field),
                 'default': field.default.__repr__,
                 'description': field.description
                 }
                for field in fields]

    def getRequiredAdapters(self):
        """Get adapters where this interface is required."""
        service = zapi.getService(self.context, 'Adapters')
        context = removeAllProxies(self.context)
        adapters = []
        for adapter in service.getRegisteredMatching(required=context):
            adapters.append({
                'provided': getPythonPath(adapter[1]),
                'required': [getPythonPath(iface) for iface in adapter[2]],
                'name': adapter[3],
                'factory': getPythonPath(adapter[4][0])
                })
        return adapters
        
    def getProvidedAdapters(self):
        """Get adapters where this interface is provided."""
        service = zapi.getService(self.context, 'Adapters')
        context = removeAllProxies(self.context)
        adapters = []
        for adapter in service.getRegisteredMatching(provided=context):
            adapters.append({
                'required': [getPythonPath(iface)
                             for iface in adapter[2]+(adapter[0],)],
                'name': adapter[3],
                'factory': getPythonPath(adapter[4][0])
                })
        return adapters

    def getFactories(self):
        """Return the factories, who will provide objects implementing this
        interface."""
        service = zapi.getService(self.context, 'Factories')
        try:
            factories = service.getFactoriesFor(removeAllProxies(self.context))
        except ComponentLookupError:
            return []
        return [{'name': n,
                 'factory': f,
                 'title': service.getFactoryInfo(n).title
                 } for n, f in factories]

    def getUtilities(self):
        """Return all utilities that provide this interface."""
        service = zapi.getService(self.context, 'Utilities')
        utils = service.getUtilitiesFor(removeAllProxies(self.context))
        return [{'name': util[0],
                 'path': getPythonPath(util[1].__class__)} for util in utils]

    def getServices(self):
        """Return all services (at most one)  that provide this interface."""
        iface = removeAllProxies(self.context)
        service = zapi.getService(self.context, 'Services')
        services = service.getServiceDefinitions()
        services = filter(lambda x: x[1] is iface, services)
        return [ser[0] for ser in services]
