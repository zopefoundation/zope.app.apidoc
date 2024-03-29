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
"""Interface Details View

"""

__docformat__ = 'restructuredtext'

import inspect

from zope.i18nmessageid import ZopeMessageFactory as _
from zope.proxy import removeAllProxies
from zope.publisher.browser import BrowserView
from zope.publisher.interfaces.browser import IBrowserRequest
from zope.publisher.interfaces.ftp import IFTPRequest
from zope.publisher.interfaces.http import IHTTPRequest
from zope.publisher.interfaces.xmlrpc import IXMLRPCRequest
from zope.security.proxy import removeSecurityProxy
from zope.traversing.api import getName
from zope.traversing.api import traverse
from zope.traversing.browser import absoluteURL

from zope.app.apidoc import classregistry
from zope.app.apidoc import component
from zope.app.apidoc import interface
from zope.app.apidoc import presentation
from zope.app.apidoc.browser.utilities import findAPIDocumentationRoot
from zope.app.apidoc.browser.utilities import findAPIDocumentationRootURL
from zope.app.apidoc.utilities import getPythonPath
from zope.app.apidoc.utilities import renderText


class InterfaceDetails(BrowserView):
    """View class for an Interface."""

    def __init__(self, context, request):
        super().__init__(context, request)
        self._prepareViews()

    def getAPIDocRootURL(self):
        return findAPIDocumentationRootURL(self.context, self.request)

    def getId(self):
        """Return the id of the field as it is defined for the interface
        utility.

        Example::

          >>> from tests import getInterfaceDetails
          >>> details = getInterfaceDetails()
          >>> details.getId()
          'IFoo'
        """
        return getName(self.context)

    def getDoc(self):
        r"""Return the main documentation string of the interface.

        Example::

          >>> from tests import getInterfaceDetails
          >>> details = getInterfaceDetails()
          >>> details.getDoc()[:55]
          u'<div class="document">\n<p>This is the Foo interface</p>'
        """
        # We must remove all proxies here, so that we get the context's
        # __module__ attribute. If we only remove security proxies, the
        # location proxy's module will be returned.
        iface = removeAllProxies(self.context)
        return renderText(iface.__doc__, inspect.getmodule(iface))

    def getBases(self):
        """Get all bases of this class

        Example::

          >>> from tests import getInterfaceDetails
          >>> details = getInterfaceDetails()
          >>> details.getBases()
          ['zope.interface.Interface']
        """
        # Persistent interfaces are security proxied, so we need to strip the
        # security proxies off
        iface = removeSecurityProxy(self.context)
        return [getPythonPath(base) for base in iface.__bases__]

    def getTypes(self):
        """Return a list of interface types that are specified for this
        interface."""
        # We have to really, really remove all proxies, since self.context (an
        # interface) is usually security proxied and location proxied. To get
        # the types, we need all proxies gone, otherwise the proxies'
        # interfaces are picked up as well.
        iface = removeAllProxies(self.context)
        return [{'name': type.getName(),
                 'path': getPythonPath(type)}
                for type in interface.getInterfaceTypes(iface)]

    def getAttributes(self):
        """Return a list of attributes in the order they were specified."""
        # The `Interface` and `Attribute` class have no security declarations,
        # so that we are not able to access any API methods on proxied
        # objects. If we only remove security proxies, the location proxy's
        # module will be returned.
        iface = removeAllProxies(self.context)
        return [interface.getAttributeInfoDictionary(attr)
                for name, attr in interface.getAttributes(iface)]

    def getMethods(self):
        """Return a list of methods in the order they were specified."""
        # The `Interface` class have no security declarations, so that we are
        # not able to access any API methods on proxied objects. If we only
        # remove security proxies, the location proxy's module will be
        # returned.
        iface = removeAllProxies(self.context)
        return [interface.getMethodInfoDictionary(method)
                for name, method in interface.getMethods(iface)]

    def getFields(self):
        r"""Return a list of fields in required + alphabetical order.

        The required attributes are listed first, then the optional
        attributes."""
        # The `Interface` class have no security declarations, so that we are
        # not able to access any API methods on proxied objects.  If we only
        # remove security proxies, the location proxy's module will be
        # returned.
        iface = removeAllProxies(self.context)
        # Make sure that the required fields are shown first
        def sorter(x): return (not x[1].required, x[0].lower())
        return [interface.getFieldInfoDictionary(field)
                for name, field in interface.getFieldsInOrder(iface, sorter)]

    def getSpecificRequiredAdapters(self):
        """Get adapters where this interface is required."""
        # Must remove security and location proxies, so that we have access to
        # the API methods and class representation.
        iface = removeAllProxies(self.context)
        regs = component.getRequiredAdapters(iface)
        regs = component.filterAdapterRegistrations(
            regs, iface,
            level=component.SPECIFIC_INTERFACE_LEVEL)
        regs = [component.getAdapterInfoDictionary(reg)
                for reg in regs]
        return regs

    def getExtendedRequiredAdapters(self):
        """Get adapters where this interface is required."""
        # Must remove security and location proxies, so that we have access to
        # the API methods and class representation.
        iface = removeAllProxies(self.context)
        regs = component.getRequiredAdapters(iface)
        regs = component.filterAdapterRegistrations(
            regs, iface,
            level=component.EXTENDED_INTERFACE_LEVEL)
        regs = [component.getAdapterInfoDictionary(reg)
                for reg in regs]
        return regs

    def getGenericRequiredAdapters(self):
        """Get adapters where this interface is required."""
        # Must remove security and location proxies, so that we have access to
        # the API methods and class representation.
        iface = removeAllProxies(self.context)
        regs = component.getRequiredAdapters(iface)
        regs = tuple(component.filterAdapterRegistrations(
            regs, iface,
            level=component.GENERIC_INTERFACE_LEVEL))
        return [component.getAdapterInfoDictionary(reg)
                for reg in regs]

    def getProvidedAdapters(self):
        """Get adapters where this interface is provided."""
        # Must remove security and location proxies, so that we have access to
        # the API methods and class representation.
        regs = component.getProvidedAdapters(removeAllProxies(self.context))
        return [component.getAdapterInfoDictionary(reg)
                for reg in regs]

    def getClasses(self):
        """Get the classes that implement this interface.

        Example::

          >>> from pprint import pprint
          >>> from tests import getInterfaceDetails
          >>> details = getInterfaceDetails()

          >>> classes = details.getClasses()
          >>> pprint(classes)
          [[('path', 'zope.app.apidoc.ifacemodule.tests.Foo'),
            ('url', 'zope/app/apidoc/ifacemodule/tests/Foo')]]
        """
        # Must remove security and location proxies, so that we have access to
        # the API methods and class representation.
        iface = removeAllProxies(self.context)
        classes = classregistry.classRegistry.getClassesThatImplement(iface)
        return [{'path': path, 'url': path.replace('.', '/')}
                for path, klass in classes]

    def getFactories(self):
        """Return the factories, who will provide objects implementing this
        interface."""
        # Must remove security and location proxies, so that we have access to
        # the API methods and class representation.
        regs = component.getFactories(removeAllProxies(self.context))
        return [component.getFactoryInfoDictionary(reg)
                for reg in regs]

    def getUtilities(self):
        """Return all utilities that provide this interface."""
        # Must remove security and location proxies, so that we have access to
        # the API methods and class representation.
        regs = component.getUtilities(removeAllProxies(self.context))
        return [component.getUtilityInfoDictionary(reg)
                for reg in regs]

    def _prepareViews(self):
        views = {IBrowserRequest: [], IXMLRPCRequest: [], IHTTPRequest: [],
                 IFTPRequest: [], None: []}
        type_map = {IBrowserRequest: 'Browser', IXMLRPCRequest: 'XMLRPC',
                    IHTTPRequest: 'HTTP', IFTPRequest: 'FTP', None: 'Other'}
        level_map = {'generic': component.GENERIC_INTERFACE_LEVEL,
                     'extended': component.EXTENDED_INTERFACE_LEVEL,
                     'specific': component.SPECIFIC_INTERFACE_LEVEL}

        iface = removeAllProxies(self.context)

        for reg in presentation.getViews(iface):
            type = presentation.getPresentationType(reg.required[-1])

            views[(type in views) and type or None].append(reg)

        for type, sel_views in views.items():
            for level, qualifier in level_map.items():
                regs = tuple(component.filterAdapterRegistrations(
                    sel_views, iface, level=qualifier))
                infos = [presentation.getViewInfoDictionary(reg)
                         for reg in regs]

                setattr(self, level + type_map[type] + 'Views', infos)

    def getViewClassTitles(self):
        return {
            "specific": _("Specific views"),
            "extended": _("Extended views"),
            "generic": _("Generic views"),
        }

    def getViewTypeTitles(self):
        return {
            "browser": _("Browser"),
            "xmlrpc": _("XML-RPC"),
            "http": _("HTTP"),
            "ftp": _("FTP"),
            "other": _("Other"),
        }


class InterfaceBreadCrumbs:
    """View that provides breadcrumbs for interface objects"""

    context = None
    request = None

    def __call__(self):
        """Create breadcrumbs for an interface object.

        The breadcrumbs are rooted at the code browser.
        """
        docroot = findAPIDocumentationRoot(self.context)
        codeModule = traverse(docroot, "Code")
        crumbs = [{
            'name': _('[top]'),
            'url': absoluteURL(codeModule, self.request)
        }]
        # We need the __module__ of the interface, not of a location proxy,
        # so we have to remove all proxies.
        iface = removeAllProxies(self.context)
        mod_names = iface.__module__.split('.')
        obj = codeModule
        for name in mod_names:
            try:
                obj = traverse(obj, name)
            except KeyError:  # pragma: no cover
                # An unknown (root) module, such as logging
                continue
            crumbs.append({
                'name': name,
                'url': absoluteURL(obj, self.request)
            })
        crumbs.append({
            'name': iface.__name__,
            'url': absoluteURL(self.context, self.request)
        })
        return crumbs
