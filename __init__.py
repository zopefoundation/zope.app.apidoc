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
"""Zope 3 API Documentation

$Id: __init__.py,v 1.5 2004/03/28 23:39:08 srichter Exp $
"""
from zope.interface import implements

from zope.app import zapi
from zope.app.location import locate
from zope.app.location.interfaces import ILocation

from interfaces import IDocumentationModule
from utilities import ReadContainerBase

class APIDocumentation(ReadContainerBase):
    r"""Represent the complete API Documentation.

    This documentation is implemented using a simply 'IReadContainer'. The
    items of the container are all registered utilities for
    IDocumentationModule.

    Demonstration::

      >>> doc = APIDocumentation(None, '++apidoc++')
      >>> doc.get('ZCML').title
      'ZCML Reference'

      >>> doc.get('Documentation') is None
      True

      >>> print '\n'.join([id for id, mod in doc.items()])
      Interface
      ZCML
    """

    implements(ILocation)

    def __init__(self, parent, name):
        self.__parent__ = parent
        self.__name__ = name
    
    def get(self, key, default=None):
        """See zope.app.container.interfaces.IReadContainer"""
        utility = zapi.queryUtility(self, IDocumentationModule, default, key)
        if utility != default:
            locate(utility, self, key)
        return utility

    def items(self):
        """See zope.app.container.interfaces.IReadContainer"""
        items = zapi.getUtilitiesFor(self, IDocumentationModule)
        items.sort()
        utils = []
        for key, value in items:
            locate(value, self, key)
            utils.append((key, value))
        return utils
        

def handleNamespace(name, parameters, pname, ob, request):
    """Used to traverse to an API Documentation."""
    return APIDocumentation(ob, pname)