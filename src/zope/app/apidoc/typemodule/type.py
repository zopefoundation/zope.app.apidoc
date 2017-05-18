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
"""Interface Types Documentation Module

"""
__docformat__ = 'restructuredtext'

from zope.interface import implementer
from zope.component import queryUtility, getUtilitiesFor
from zope.i18nmessageid import ZopeMessageFactory as _
from zope.interface.interfaces import IInterface
from zope.location import LocationProxy
from zope.location.interfaces import ILocation

from zope.app.apidoc.interfaces import IDocumentationModule
from zope.app.apidoc.utilities import ReadContainerBase


@implementer(ILocation)
class TypeInterface(ReadContainerBase):
    """Representation of the special type interface.

    Demonstration::

      >>> from zope.interface import Interface
      >>> class IFoo(Interface):
      ...    pass
      >>> @implementer(IFoo)
      ... class Foo(object):
      ...     def getName(self):
      ...         return 'IFoo'
      >>> from zope import component as ztapi
      >>> ztapi.provideUtility(Foo(), IFoo, 'Foo')

      >>> typeiface = TypeInterface(IFoo, None, None)
      >>> typeiface.interface
      <InterfaceClass zope.app.apidoc.typemodule.type.IFoo>

      >>> typeiface.get('Foo').__class__ == Foo
      True

      >>> typeiface.items()
      [(u'Foo', <zope.app.apidoc.typemodule.type.Foo object at ...>)]

    """

    def __init__(self, interface, parent, name):
        self.__parent__ = parent
        self.__name__ = name
        self.interface = interface

    def get(self, key, default=None):
        """See zope.container.interfaces.IReadContainer"""
        return LocationProxy(
            queryUtility(self.interface, key, default=default),
            self, key)

    def items(self):
        """See zope.container.interfaces.IReadContainer"""
        results = [(name, LocationProxy(iface, self, name))
                   for name, iface in getUtilitiesFor(self.interface)]
        results.sort(key=lambda x: (x[1].getName(), x[0]))
        return results


@implementer(IDocumentationModule)
class TypeModule(ReadContainerBase):
    r"""Represent the Documentation of all interface types.

    Demonstration::

      >>> class IFoo(IInterface):
      ...    pass

      >>> from zope import component as ztapi
      >>> ztapi.provideUtility(IFoo, IInterface, 'IFoo')

      >>> module = TypeModule()
      >>> type = module.get('IFoo')

      >>> type.interface
      <InterfaceClass zope.app.apidoc.typemodule.type.IFoo>

      >>> [type.interface for name, type in module.items()]
      [<InterfaceClass zope.app.apidoc.typemodule.type.IFoo>]
    """

    # See zope.app.apidoc.interfaces.IDocumentationModule
    title = _('Interface Types')

    # See zope.app.apidoc.interfaces.IDocumentationModule
    description = _("""
    Here you can see all registered interface types. When you open the subtree
    of a specific interface type, you can see all the interfaces that provide
    this type. This can be very useful in cases where you want to determine
    all content type interfaces, for example.
    """)

    __name__ = None
    __parent__ = None

    def get(self, key, default=None):
        return TypeInterface(
            queryUtility(IInterface, key, default=default), self, key)

    def items(self):
        results = [(name, TypeInterface(iface, self, name))
                   for name, iface in getUtilitiesFor(IInterface)
                   if iface.extends(IInterface)]
        results.sort(key=lambda x: x[1].interface.getName())
        return results
