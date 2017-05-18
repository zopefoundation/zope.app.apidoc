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

    def __locate(self, obj, name):
        # In general, *always* doing this is not just weird (threads), it also leads to
        # circular __parent__ chains, which causes issues with things like
        # zope.securitypolicy
        # (https://github.com/zopefoundation/zope.securitypolicy/issues/8), and
        # it can lead to bad behaviour with sharing persistent objects
        # across ZODB connections (which may close). Fortunately, our traverser
        # takes care of this by making sure we are always located at an (equivalent)
        # fresh root.
        locate(obj, self, name)
        return obj

    def get(self, key, default=None):
        """See zope.container.interfaces.IReadContainer"""
        utility = zope.component.queryUtility(IDocumentationModule, key, default)
        if utility is not default:
            utility = self.__locate(utility, key)
        return utility

    def items(self):
        """See zope.container.interfaces.IReadContainer"""
        items = sorted(zope.component.getUtilitiesFor(IDocumentationModule))
        utils = []
        for key, value in items:
            utils.append((key, self.__locate(value, key)))
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
    # Ignore the `ob` we traverse through. We always want to be
    # located at the root, although not the *actual* root.
    # This is because we have to reparent our children, which are
    # shared, in-memory utilities, and in the presence of multiple threads,
    # doing so at different times would be bad in case connections get closed.
    # So we make a pseudo root.
    from zope.site.folder import rootFolder
    ob = rootFolder()
    return APIDocumentation(ob, '++apidoc++' + name)
