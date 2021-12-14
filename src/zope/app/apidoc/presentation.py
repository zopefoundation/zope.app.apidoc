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
"""Views/Presentation Utilities

"""
import six
from zope.component import getGlobalSiteManager
from zope.interface import Interface

from zope.i18nmessageid import ZopeMessageFactory as _
from zope.app.apidoc.utilities import getPythonPath, relativizePath
from zope.app.apidoc.utilities import getPermissionIds
from zope.app.apidoc.component import getParserInfoInfoDictionary
from zope.app.apidoc.component import getInterfaceInfoDictionary
from zope.browserresource.icon import IconViewFactory

from zope.publisher.interfaces import IRequest
from zope.publisher.interfaces.browser import IBrowserRequest
from zope.publisher.interfaces.xmlrpc import IXMLRPCRequest
from zope.publisher.interfaces.http import IHTTPRequest
from zope.publisher.interfaces.ftp import IFTPRequest


SPECIFIC_INTERFACE_LEVEL = 1
EXTENDED_INTERFACE_LEVEL = 2
GENERIC_INTERFACE_LEVEL = 4

BROWSER_DIRECTIVES_MODULE = 'zope.app.publisher.browser.viewmeta'
XMLRPC_DIRECTIVES_MODULE = 'zope.app.publisher.xmlrpc.metaconfigure'
JSONRPC_DIRECTIVES_MODULE = 'jsonserver.metaconfigure'


def getViewFactoryData(factory):
    """Squeeze some useful information out of the view factory"""
    info = {'path': None, 'url': None, 'template': None, 'resource': None,
            'referencable': True}

    # Always determine the most basic factory
    # Commonly, factories are wrapped to provide security or location, for
    # example. If those wrappers play nice, then they provide a `factory`
    # attribute, that points to the original factory.
    while hasattr(factory, 'factory'):
        factory = factory.factory

    if getattr(factory, '__name__', '').startswith('SimpleViewClass'):
        # In the case of a SimpleView, the base is really what we are
        # interested in. Usually the first listed class is the interesting one.
        base = factory.__bases__[0]
        info['path'] = base.__module__ + '.' + base.__name__
        info['template'] = relativizePath(factory.index.filename)
        info['template_obj'] = factory.index

    # Basic Type is a factory
    elif isinstance(factory, (six.string_types, float, int, list, tuple)):
        info['referencable'] = False

    elif factory.__module__ is not None:
        if factory.__module__.startswith(BROWSER_DIRECTIVES_MODULE):
            info['path'] = getPythonPath(factory.__bases__[0])
        # XML-RPC view factory, generated during registration
        elif (factory.__module__.startswith(XMLRPC_DIRECTIVES_MODULE)
              # JSON-RPC view factory, generated during registration
              # This is needed for the 3rd party jsonserver implementation
              # TODO: See issue http://www.zope.org/Collectors/Zope3-dev/504,
              # ri
              or factory.__module__.startswith(JSONRPC_DIRECTIVES_MODULE)):
            # Those factories are method publisher and security wrapped
            info['path'] = getPythonPath(factory.__bases__[0].__bases__[0])

    if not info['path'] and not hasattr(factory, '__name__'):
        # A factory that is a class instance; since we cannot reference
        # instances, reference the class.
        info['path'] = getPythonPath(factory.__class__)

    if not info['path']:
        # Either a simple class-based factory, or not. It doesn't
        # matter. We have tried our best; just get the Python path as
        # good as you can.
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
    for kind in [IBrowserRequest, IXMLRPCRequest, IHTTPRequest, IFTPRequest]:
        if iface.isOrExtends(kind):
            return kind
    return iface


def getViews(iface, type=IRequest):
    """Get all view registrations for a particular interface."""
    gsm = getGlobalSiteManager()
    for reg in gsm.registeredAdapters():
        if (reg.required and
            reg.required[-1] is not None and
                reg.required[-1].isOrExtends(type)):

            for required_iface in reg.required[:-1]:
                if required_iface is None or iface.isOrExtends(required_iface):
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
    if isinstance(reg.info, six.string_types):
        doc = reg.info
        zcml = None
    else:
        doc = None
        zcml = getParserInfoInfoDictionary(reg.info)

    info = {'name': six.text_type(reg.name) or _('<i>no name</i>'),
            'type': getPythonPath(getPresentationType(reg.required[-1])),
            'factory': getViewFactoryData(reg.factory),
            'required': [getInterfaceInfoDictionary(iface)
                         for iface in reg.required],
            'provided': getInterfaceInfoDictionary(reg.provided),
            'doc': doc,
            'zcml': zcml
            }

    # Educated guess of the attribute name
    info.update(getPermissionIds('publishTraverse', klass=reg.factory))

    return info
