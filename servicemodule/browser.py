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
"""Service Details View

$Id$
"""
from zope.app import zapi
from zope.app.location import LocationProxy
from zope.app.apidoc.ifacemodule.browser import InterfaceDetails
from zope.app.apidoc.utilities import getPythonPath

class Menu(object):
    """Menu View Helper Class

    'node' is a 'zope.app.tree.node.Node' instance.

    Examples::

      >>> from zope.component.interfaces import IUtilityService
      >>> from zope.component.utility import GlobalUtilityService
      >>> from zope.app.tree.node import Node 
      >>> from zope.app.apidoc.servicemodule import ServiceModule, Service
      >>> from zope.app.apidoc.tests import Root

      >>> servicemod = ServiceModule()
      >>> servicemod.__name__ = 'Services'
      >>> servicemod.__parent__ = Root()
      >>> service = Service(servicemod, 'Utilities', IUtilityService,
      ...                   [GlobalUtilityService])
      >>> menu = Menu()

      >>> node = Node(service)
      >>> menu.getMenuTitle(node)
      'Utilities'

      >>> menu.getMenuLink(node)
      './Utilities/index.html'
    """

    def getMenuTitle(self, node):
        """Return the title of the node that is displayed in the menu."""
        return zapi.name(node.context)

    def getMenuLink(self, node):
        """Return the HTML link of the node that is displayed in the menu."""
        return './'+ zapi.name(node.context) + '/index.html'


class ServiceDetails(object):
    """View for a Service in the API Documentation

    Example::
    
      >>> from zope.app.apidoc.tests import pprint
      >>> from zope.component.interfaces import IUtilityService
      >>> from zope.component.utility import GlobalUtilityService
      >>> from zope.publisher.browser import TestRequest
      >>> from zope.app.tree.node import Node 
      >>> from zope.app.apidoc.servicemodule import ServiceModule, Service
      >>> from zope.app.apidoc.tests import Root
    
      >>> servicemod = ServiceModule()
      >>> servicemod.__name__ = 'Services'
      >>> servicemod.__parent__ = Root()
      >>> service = Service(servicemod, 'Utilities', IUtilityService,
      ...                   [GlobalUtilityService()])
      >>> details = ServiceDetails()
      >>> details.context = service
      >>> details.request = TestRequest()

      >>> iface = details.interface()
      >>> iface.getId()
      'zope.component.interfaces.IUtilityService'

      >>> impl = details.implementations()
      >>> pprint(impl)
      [[('path', 'zope.component.utility.GlobalUtilityService'),
        ('url', 'zope/component/utility/GlobalUtilityService')]]
    """

    def interface(self):
        """Get the details view of the interface the service provides."""
        iface = LocationProxy(self.context.interface,
                               self.context,
                               getPythonPath(self.context.interface))
        details = InterfaceDetails()
        details.context = iface
        details.request = self.request
        return details
    
    def implementations(self):
        """Retrieve a list of implementations of this service."""
        impl = [impl.__class__ for impl in self.context.implementations]
        return [{'path': getPythonPath(klass),
                 'url': getPythonPath(klass).replace('.', '/')}
                for klass in impl]
