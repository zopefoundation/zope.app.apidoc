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
"""ZCML Documentation module

The ZCML documentation module reads all of the meta directives (but does not
execute them) and uses the collected data to generate the tree. The result of
the evaluation is stored in thread-global variables, so that we have to parse
the files only once.

"""
from zope.testing.cleanup import addCleanUp


__docformat__ = 'restructuredtext'

import zope.app.appsetup.appsetup
from zope.configuration import docutils
from zope.i18nmessageid import ZopeMessageFactory as _
from zope.interface import implementer
from zope.location.interfaces import ILocation

from zope.app.apidoc.interfaces import IDocumentationModule
from zope.app.apidoc.utilities import DocumentationModuleBase
from zope.app.apidoc.utilities import ReadContainerBase


# Caching variables, so that the meta-ZCML files need to be read only once
namespaces = None
subdirs = None


def quoteNS(ns):
    """Quotes a namespace to make it URL-secure."""
    ns = ns.replace(':', '_co_')
    ns = ns.replace('/', '_sl_')
    return ns


def unquoteNS(ns):
    """Un-quotes a namespace from a URL-secure version."""
    ns = ns.replace('_sl_', '/')
    ns = ns.replace('_co_', ':')
    return ns


@implementer(ILocation)
class Namespace(ReadContainerBase):
    """Simple namespace object for the ZCML Documentation Module.

    This container has :class:`Directive` items as its values.
    """

    def __init__(self, parent, name):
        self.__parent__ = parent
        self.__realname__ = name
        self.__name__ = self.getQuotedName()

    def getShortName(self):
        """Get the short name of the namespace."""
        name = self.__realname__
        if name.startswith('http://namespaces.zope.org/'):
            name = name[27:]
        return name

    def getFullName(self):
        """Get the full name of the namespace."""
        return self.__realname__

    def getQuotedName(self):
        """Get the full name, but quoted for a URL."""
        name = self.getFullName()
        name = quoteNS(name)
        return name

    def get(self, key, default=None):
        _makeDocStructure()
        ns = self.getFullName()
        if key not in namespaces[ns]:
            return default
        schema, handler, info = namespaces[ns][key]
        sd = subdirs.get((ns, key), [])
        directive = Directive(self, key, schema, handler, info, sd)
        return directive

    def items(self):
        _makeDocStructure()
        return sorted((key, self.get(key))
                      for key
                      in namespaces[self.getFullName()].keys())


@implementer(ILocation)
class Directive:
    """Represents a ZCML Directive."""

    def __init__(self, ns, name, schema, handler, info, subdirs):
        self.__parent__ = ns
        self.__name__ = name
        self.schema = schema
        self.handler = handler
        self.info = info
        self.subdirs = subdirs


@implementer(IDocumentationModule)
class ZCMLModule(DocumentationModuleBase):
    r"""
    Represent the Documentation of all ZCML namespaces.

    The items of the container are tuples of globally known namespaces
    found in the :func:`appsetup config context
    <zope.app.appsetup.appsetup.getConfigContext>`.
    """

    #: Title.
    title = _('ZCML Reference')

    #: Description.
    description = _("""
    This module presents you with a complete list of ZCML directives and
    serves therefore well as reference. The menu provides you with a tree that
    organizes the directives by namespaces.

    The documentation contents for each directive tells you all the available
    attributes and their semantics. It also provides a link to the interface
    the directive confirms to. If available, it will even tell you the
    file the directive was declared in. At the end a list of available
    subdirectives is given, also listing the implemented interface and
    available attributes.
    """)

    def get(self, key, default=None):
        """Get the namespace by name; long and abbreviated names work.
        """
        _makeDocStructure()

        key = unquoteNS(key)
        if key in namespaces:
            return Namespace(self, key)

        # TODO: Search for other packages outside this root.
        full_key = 'http://namespaces.zope.org/' + key
        if full_key in namespaces:
            return Namespace(self, full_key)

        return default

    def items(self):
        _makeDocStructure()
        result = []
        for key in namespaces:
            namespace = Namespace(self, key)
            # We need to make sure that we use the quoted URL as key
            result.append((namespace.getQuotedName(), namespace))
        result.sort()
        return result


def _makeDocStructure():
    # Some trivial caching
    global namespaces
    global subdirs
    if namespaces is not None and subdirs is not None:
        return

    context = zope.app.appsetup.appsetup.getConfigContext()
    assert context is not None
    namespaces, subdirs = docutils.makeDocStructures(context)

    # Empty keys are not so good for a container
    if '' in namespaces:
        namespaces['ALL'] = namespaces['']
        del namespaces['']


def _clear():
    global namespaces
    global subdirs
    namespaces = None
    subdirs = None


addCleanUp(_clear)
