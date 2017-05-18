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
"""Utility Documentation Module


"""
__docformat__ = 'restructuredtext'

import base64
import binascii

import zope.component

from zope.interface import implementer
from zope.location.interfaces import ILocation

from zope.i18nmessageid import ZopeMessageFactory as _
from zope.app.apidoc.interfaces import IDocumentationModule
from zope.app.apidoc.utilities import ReadContainerBase, getPythonPath
from zope.app.apidoc.utilities import DocumentationModuleBase

# Constant used when the utility has no name
NONAME = '__noname__'

def encodeName(name):
    name = base64.urlsafe_b64encode(name.encode('utf-8'))
    if not isinstance(name, str):
        name = name.decode('ascii')
    return name

def decodeName(name):
    try:
        to_decode = name
        if not isinstance(to_decode, bytes):
            to_decode = to_decode.encode("ascii")

        return base64.urlsafe_b64decode(to_decode).decode('utf-8')
    except (binascii.Error, TypeError):
        # Someone probably passed a non-encoded name, so let's accept that.
        return name


@implementer(ILocation)
class Utility(object):
    """Representation of a utility for the API Documentation"""

    def __init__(self, parent, reg):
        """Initialize Utility object."""
        self.__parent__ = parent
        self.__name__ = encodeName(reg.name or NONAME)
        self.name = reg.name or NONAME
        self.registration = reg
        self.interface = reg.provided
        self.component = reg.component
        self.doc = reg.info


@implementer(ILocation)
class UtilityInterface(ReadContainerBase):
    """Representation of an interface a utility provides."""

    def __init__(self, parent, name, interface):
        self.__parent__ = parent
        self.__name__ = name
        self.interface = interface

    def get(self, key, default=None):
        """See zope.container.interfaces.IReadContainer"""
        sm = zope.component.getGlobalSiteManager()
        key = decodeName(key)
        if key == NONAME:
            key = ''
        utils = [Utility(self, reg)
                 for reg in sm.registeredUtilities()
                 if reg.name == key and reg.provided == self.interface]
        return utils[0] if utils else default

    def items(self):
        """See zope.container.interfaces.IReadContainer"""
        sm = zope.component.getGlobalSiteManager()
        items = [(encodeName(reg.name or NONAME), Utility(self, reg))
                 for reg in sm.registeredUtilities()
                 if self.interface == reg.provided]
        return sorted(items)


@implementer(IDocumentationModule)
class UtilityModule(DocumentationModuleBase):
    """Represent the Documentation of all Interfaces.

    This documentation is implemented using a simple `IReadContainer`. The
    items of the container are all utility interfaces.
    """

    # See zope.app.apidoc.interfaces.IDocumentationModule
    title = _('Utilities')

    # See zope.app.apidoc.interfaces.IDocumentationModule
    description = _("""
    Utilities are also nicely registered in a site manager, so that it is easy
    to create a listing of available utilities. A utility is identified by the
    providing interface and a name, which can be empty. The menu provides you
    with a list of interfaces that utilities provide and as sub-items the
    names of the various implementations.

    Again, the documentation of a utility lists all the attributes/fields and
    methods the utility provides and provides a link to the implementation.
    """)

    def get(self, key, default=None):
        parts = key.split('.')
        try:
            mod = __import__('.'.join(parts[:-1]), {}, {}, ('*',))
        except ImportError:
            return default
        else:
            return UtilityInterface(self, key, getattr(mod, parts[-1], default))

    def items(self):
        # Use a list of site managers, since we want to support multiple bases
        smlist = [zope.component.getSiteManager()]
        seen = []
        ifaces = {}
        while smlist:
            # Get the next site manager
            sm = smlist.pop()
            # If we have already looked at this site manager, then skip it
            if sm in seen: # pragma: no cover
                continue
            # Add the current site manager to the list of seen ones
            seen.append(sm)
            # Add the bases of the current site manager to the list of site
            # managers to be processed
            smlist += list(sm.__bases__)
            for reg in sm.registeredUtilities():
                path = getPythonPath(reg.provided)
                ifaces[path] = UtilityInterface(self, path, reg.provided)

        items = sorted(ifaces.items(),
                       key=lambda x:x[0].split('.')[-1])
        return items
