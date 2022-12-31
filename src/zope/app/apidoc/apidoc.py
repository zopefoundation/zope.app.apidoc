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
from zope.location.interfaces import ILocation
from zope.publisher.browser import applySkin

from zope.app.apidoc.interfaces import IDocumentationModule
from zope.app.apidoc.utilities import ReadContainerBase


@implementer(ILocation)
class APIDocumentation(ReadContainerBase):
    """
    The collection of all API documentation.

    This documentation is implemented using a simply
    :class:`~zope.container.interfaces.IReadContainer`. The items of
    the container are all registered utilities for
    :class:`~zope.app.apidoc.interfaces.IDocumentationModule`.
    """

    def __init__(self, parent, name):
        self.__parent__ = parent
        self.__name__ = name

    # We must always be careful to return copies that are located beneath us.
    # We can't return the original because they're expected to be shared in
    # memory and mutating their parentage causes issues with crossing ZODB
    # connections and even circular parentage. Returning a
    # :class:`~.LocationProxy` doesn't work because URLs the utility wants to
    # generate can't find a parent.

    def get(self, key, default=None):
        """
        Look up an ``IDocumentationModule`` utility with the given name.

        If found, a copy of the utility with this object as its
        parent, created by
        :meth:`~zope.app.apidoc.interfaces.IDocumentationModule.withParentAndName`,
        will be returned.
        """  # noqa: E501 line too long
        utility = zope.component.queryUtility(
            IDocumentationModule, key, default)
        if utility is not default:
            utility = utility.withParentAndName(self, key)
        return utility

    def items(self):
        """
        Return a sorted list of `(name, utility)` pairs for all registered
        :class:`~.IDocumentationModule` objects.

        Each utility returned will be a child of this object created with
        :meth:`~zope.app.apidoc.interfaces.IDocumentationModule.withParentAndName`.
        """
        items = sorted(zope.component.getUtilitiesFor(IDocumentationModule))
        return [(key, value.withParentAndName(self, key))
                for key, value
                in items]


class apidocNamespace:
    """Used to traverse to an API Documentation.

    Instantiating this object with a request will apply the
    :class:`zope.app.apidoc.browser.skin.APIDOC` skin automatically.
    """

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
