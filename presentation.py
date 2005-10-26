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
"""Views/Presentation Utilities

$Id$
"""
from types import ClassType, FunctionType
from zope.component.site import AdapterRegistration
from zope.interface import Interface

from zope.app import zapi
from zope.app.apidoc.utilities import getPythonPath, relativizePath
from zope.app.apidoc.utilities import getPermissionIds
from zope.app.apidoc.component import getParserInfoInfoDictionary
from zope.app.apidoc.component import getInterfaceInfoDictionary
from zope.app.publisher.browser.icon import IconViewFactory

from zope.publisher.interfaces import IRequest, ILayer
from zope.publisher.interfaces.browser import IBrowserRequest
from zope.publisher.interfaces.xmlrpc import IXMLRPCRequest
from zope.publisher.interfaces.http import IHTTPRequest
from zope.publisher.interfaces.ftp import IFTPRequest

SPECIFIC_INTERFACE_LEVEL = 1
EXTENDED_INTERFACE_LEVEL = 2
GENERIC_INTERFACE_LEVEL = 4

BROWSER_DIRECTIVES_MODULE = 'zope.app.publisher.browser.viewmeta'
XMLRPC_DIRECTIVES_MODULE = 'zope.app.publisher.xmlrpc.metaconfigure'

def getViewFactoryData(factory):
    """Squeeze some useful information out of the view factory"""
    info = {'path': None, 'url': None, 'template': None, 'resource': None,
            'referencable': True}

    if hasattr(factory, '__name__') and \
       factory.__name__.startswith('SimpleViewClass'):
        # In the case of a SimpleView, the base is really what we are
        # interested in. Usually the first listed class is the interesting one.
        base = factory.__bases__[0]
        info['path'] = base.__module__ + '.' + base.__name__
        info['template'] = relativizePath(factory.index.filename)

    # Basic Type is a factory
    elif isinstance(factory, (str, unicode, float, int, list, tuple)):
        info['referencable'] = False

    elif factory.__module__ is not None and \
             factory.__module__.startswith(BROWSER_DIRECTIVES_MODULE):
        info['path'] = getPythonPath(factory.__bases__[0])

    # XML-RPC view factory, generated during registration
    elif factory.__module__ is not None and \
             factory.__module__.startswith(XMLRPC_DIRECTIVES_MODULE):

        # Those factories are method publisher and security wrapped
        info['path'] = getPythonPath(factory.__bases__[0].__bases__[0])

    # Special for views registered with the zope:view directive; the proxy
    # view implements the security wrapping
    elif hasattr(factory, '__class__') and \
             factory.__class__.__name__ == 'ProxyView':
        factory = factory.factory
        info['path'] = factory.__module__ + '.' + factory.__name__

    # A factory that is a class instance; since we cannot reference instances,
    # reference the class.
    elif not hasattr(factory, '__name__'):
        info['path'] = getPythonPath(factory.__class__)

    # A simple class-based factory
    elif type(factory) in (type, ClassType):
        info['path'] = getPythonPath(factory)

    # Sometimes factories are functions; there are two cases: (1) the factory
    # itself is a function, and (2) the original factory was wrapped by a
    # function; in the latter case the function must have a `factory`
    # attribute that references the original factory
    elif isinstance(factory, FunctionType):
        info['path'] = getPythonPath(getattr(factory, 'factory', factory))

    # We have tried our best; just get the Python path as good as you can.
    else:
        info['path'] = getPythonPath(factory)

    if info['referencable']:
        info['url'] = info['path'].replace('.', '/')

    if isinstance(factory, IconViewFactory):
        info['resource'] = factory.rname

    return info


def getPresentationType(iface):
    """Get the presentation type from a layer interface."""
    # Note that the order of the requests matters here, since we want to
    # inspect the most specific one first. For example, IBrowserRequest is also
    # an IHTTPRequest.
    for type in [IBrowserRequest, IXMLRPCRequest, IHTTPRequest, IFTPRequest]:
        if iface.isOrExtends(type):
            return type
    return iface


def getViews(iface, type=IRequest):
    """Get all view registrations for a particular interface."""
    gsm = zapi.getGlobalSiteManager()
    for reg in gsm.registrations():
        if (isinstance(reg, AdapterRegistration) and
            len(reg.required) > 0 and
            reg.required[-1] is not None and
            reg.required[-1].isOrExtends(type)):

            for required_iface in reg.required[:-1]:
                if iface.isOrExtends(required_iface):
                    yield reg


def filterViewRegistrations(regs, iface, level=SPECIFIC_INTERFACE_LEVEL):
    """Return only those registrations that match the specifed level"""
    for reg in regs:
        if level & GENERIC_INTERFACE_LEVEL:
            for required_iface in reg.required[:-1]:
                if required_iface in (Interface, None):
                    yield reg
                    continue

        if level & EXTENDED_INTERFACE_LEVEL:
            for required_iface in reg.required[:-1]:
                if required_iface is not Interface and \
                       iface.extends(required_iface):
                    yield reg
                    continue

        if level & SPECIFIC_INTERFACE_LEVEL:
            for required_iface in reg.required[:-1]:
                if required_iface is iface:
                    yield reg
                    continue


def getViewInfoDictionary(reg):
    """Build up an information dictionary for a view registration."""
    # get configuration info
    if isinstance(reg.doc, (str, unicode)):
        doc = reg.doc
        zcml = None
    else:
        doc = None
        zcml = getParserInfoInfoDictionary(reg.doc)

    # get layer
    layer = None
    if ILayer.providedBy(reg.required[-1]):
        layer = getInterfaceInfoDictionary(reg.required[-1])


    info = {'name' : reg.name or '<i>no name</i>',
            'type' : getPythonPath(getPresentationType(reg.required[-1])),
            'factory' : getViewFactoryData(reg.value),
            'required': [getInterfaceInfoDictionary(iface)
                         for iface in reg.required],
            'provided' : getInterfaceInfoDictionary(reg.provided),
            'layer': layer,
            'doc': doc,
            'zcml': zcml
            }

    # Educated guess of the attribute name
    info.update(getPermissionIds('publishTraverse', klass=reg.value))

    return info
