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
"""Service Documentation Module

$Id$
"""
__docformat__ = 'restructuredtext'

from zope.interface import implements
from zope.component import ComponentLookupError

from zope.app import zapi
from zope.app.location.interfaces import ILocation
from zope.app.apidoc.interfaces import IDocumentationModule
from zope.app.apidoc.utilities import ReadContainerBase
from zope.app.servicenames import Services
from zope.app.i18n import ZopeMessageIDFactory as _

class Service(object):
    """Object representing a service in the API documentation"""

    implements(ILocation)

    def __init__(self, parent, name, iface, impl):
        """Initialize Service object."""
        self.__parent__ = parent
        self.__name__ = name
        self.interface = iface
        self.implementations = impl


class ServiceModule(ReadContainerBase):
    r"""Represent the Documentation of all Interfaces.

    This documentation is implemented using a simply 'IReadContainer'. The
    items of the container are all the interfaces listed in the closest
    interface service and above.

    Demonstration::

      >>> from zope.app.tests import placelesssetup as setup
      >>> setup.setUp()

      >>> module = ServiceModule()

      >>> module.get('Utilities').__name__
      'Utilities'

      >>> module.get('foo') is None
      True
      
      >>> print '\n'.join([id for id, iface in module.items()][:4])
      Adapters
      Presentation
      Services
      Utilities
      
      >>> setup.tearDown()
    """

    implements(IDocumentationModule)

    # See zope.app.apidoc.interfaces.IDocumentationModule
    title = _('Services')

    # See zope.app.apidoc.interfaces.IDocumentationModule
    description = _("""
    The services module let's the reader browse through all defined
    services. It uses the service name as a key. In general services can be
    queried using::

      >>> from zope.app import zapi
      >>> service = zapi.getService('ServiceName')

    Here we used 'None' as the context by default, which means that
    always a global service is returned. If you use an object that has
    a location in the traversal tree, you will generally get the closest
    service, which includes the local ones. The first argument is the
    service name, which you can replace with any name listed in this
    module's menu.

    For each service, the attributes and methods of the service interface are
    presented. At the end a list of implementations is given.
    """)

    def get(self, key, default=None):
        """See zope.app.container.interfaces.IReadContainer"""
        service = zapi.getService(Services)
        items = service.getServiceDefinitions()

        for name, iface in items:
            if name == key:
                try:
                    impl = service.getService(name)
                except ComponentLookupError:
                    impl = None
                return Service(self, name, iface, [impl])

        return default

    def items(self):
        """See zope.app.container.interfaces.IReadContainer"""
        service = zapi.getService(Services)
        items = service.getServiceDefinitions()
        items.sort()
        return [(name, self.get(name)) for name, iface in items]
