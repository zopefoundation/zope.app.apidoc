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
"""Class representation for code browser
"""

__docformat__ = 'restructuredtext'

from inspect import isfunction
from inspect import ismethod
from inspect import ismethoddescriptor

from zope.interface import implementedBy
from zope.interface import implementer
from zope.location.interfaces import ILocation
from zope.security.checker import getCheckerForInstancesOf

from zope.app.apidoc.classregistry import classRegistry
from zope.app.apidoc.codemodule.interfaces import IClassDocumentation
from zope.app.apidoc.utilities import getInterfaceForAttribute
from zope.app.apidoc.utilities import getPublicAttributes


@implementer(ILocation, IClassDocumentation)
class Class(object):
    """This class represents a class declared in the module."""

    def __init__(self, module, name, klass):
        self.__parent__ = module
        self.__name__ = name
        self.__klass = klass

        # Setup interfaces that are implemented by this class.
        self.__interfaces = tuple(implementedBy(klass))
        self.__all_ifaces = tuple(implementedBy(klass).flattened())

        # Register the class with the global class registry.
        classRegistry[self.getPath()] = klass

    def getPath(self):
        """See :class:`~zope.app.apidoc.codemodule.interfaces.IClassDocumentation`."""  # noqa: E501 line too long
        return self.__parent__.getPath() + '.' + self.__name__

    def getDocString(self):
        """See :class:`~zope.app.apidoc.codemodule.interfaces.IClassDocumentation`."""  # noqa: E501 line too long
        return self.__klass.__doc__

    def getBases(self):
        """See :class:`~zope.app.apidoc.codemodule.interfaces.IClassDocumentation`."""  # noqa: E501 line too long
        return self.__klass.__bases__

    def getKnownSubclasses(self):
        """See :class:`~zope.app.apidoc.codemodule.interfaces.IClassDocumentation`."""  # noqa: E501 line too long
        return [k for n, k in classRegistry.getSubclassesOf(self.__klass)]

    def getInterfaces(self):
        """See :class:`~zope.app.apidoc.codemodule.interfaces.IClassDocumentation`."""  # noqa: E501 line too long
        return self.__interfaces

    def _iterAllAttributes(self):
        for name in getPublicAttributes(self.__klass):
            iface = getInterfaceForAttribute(
                name, self.__all_ifaces, asPath=False)
            yield name, getattr(self.__klass, name), iface

    if str is bytes:
        # Python 2
        _ismethod = staticmethod(ismethod)
    else:
        # On Python 3, there is no unbound method. But we can't treat
        # things that are simply callable as methods. Things like the
        # security proxy are callable, but when `permission =
        # CheckerPublic` (where zope.security.checker.CheckerPublic is
        # proxied) is a class attribute, that's *not* a method.
        # Checking if its actually a function gets us much more accurate
        # results. (We could also check its qualname to see if it "belongs"
        # to this class, but this seems to do the trick)
        _ismethod = staticmethod(isfunction)

    def getAttributes(self):
        """See :class:`~zope.app.apidoc.codemodule.interfaces.IClassDocumentation`."""  # noqa: E501 line too long
        return [(name, obj, iface)
                for name, obj, iface in self._iterAllAttributes()
                if not self._ismethod(obj) and not ismethoddescriptor(obj)]

    def getMethods(self):
        """See :class:`~zope.app.apidoc.codemodule.interfaces.IClassDocumentation`."""  # noqa: E501 line too long
        return [(name, obj, iface)
                for name, obj, iface in self._iterAllAttributes()
                if self._ismethod(obj)]

    def getMethodDescriptors(self):
        return [(name, obj, iface)
                for name, obj, iface in self._iterAllAttributes()
                if ismethoddescriptor(obj)]

    def getSecurityChecker(self):
        """See :class:`~zope.app.apidoc.codemodule.interfaces.IClassDocumentation`."""  # noqa: E501 line too long
        return getCheckerForInstancesOf(self.__klass)

    def getConstructor(self):
        """See :class:`~zope.app.apidoc.codemodule.interfaces.IClassDocumentation`."""  # noqa: E501 line too long
        init = getattr(self.__klass, '__init__', None)
        if callable(init):
            return init
