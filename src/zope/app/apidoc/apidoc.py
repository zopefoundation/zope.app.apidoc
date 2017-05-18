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
"""Zope 3 API Documentation

"""
__docformat__ = 'restructuredtext'

import zope.component
from zope.interface import implementer
from zope.publisher.browser import applySkin
from zope.location import locate
from zope.location.interfaces import ILocation

from zope.app.apidoc.interfaces import IDocumentationModule
from zope.app.apidoc.utilities import ReadContainerBase

@implementer(ILocation)
class APIDocumentation(ReadContainerBase):
    """Represent the complete API Documentation.

    This documentation is implemented using a simply `IReadContainer`. The
    items of the container are all registered utilities for
    `IDocumentationModule`.
    """

    def __init__(self, parent, name):
        self.__parent__ = parent
        self.__name__ = name

    # We must always be careful to return copies that are located beneath us.
    # We can't return the original because they're expected to be shared in memory
    # and mutating their parentage causes issues with crossing ZODB connections
    # and even circular parentage.

    def get(self, key, default=None):
        """See zope.container.interfaces.IReadContainer"""
        utility = zope.component.queryUtility(IDocumentationModule, key, default)
        if utility is not default:
            utility = utility.withParentAndName(self, key)
        return utility

    def items(self):
        """See zope.container.interfaces.IReadContainer"""
        items = sorted(zope.component.getUtilitiesFor(IDocumentationModule))
        utils = []
        for key, value in items:
            utils.append((key, value.withParentAndName(self, key)))
        return utils


class apidocNamespace(object):
    """Used to traverse to an API Documentation."""
    def __init__(self, ob, request=None):
        if request:
            from zope.app.apidoc.browser.skin import APIDOC
            applySkin(request, APIDOC)
        self.context = ob

    def traverse(self, name, ignore):
        return handleNamespace(self.context, name)

def handleNamespace(ob, name):
    """Used to traverse to an API Documentation."""
    return APIDocumentation(ob, '++apidoc++' + name)
