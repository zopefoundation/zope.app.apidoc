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
"""Class representation for code browser 

$Id: __init__.py 29143 2005-02-14 22:43:16Z srichter $
"""
__docformat__ = 'restructuredtext'
import inspect

from zope.interface import implements, implementedBy
from zope.security.checker import getCheckerForInstancesOf
from zope.app.location.interfaces import ILocation

from zope.app.apidoc.classregistry import classRegistry
from zope.app.apidoc.utilities import getInterfaceForAttribute
from zope.app.apidoc.utilities import getPublicAttributes
from zope.app.apidoc.utilities import getPythonPath
from interfaces import IClassDocumentation

class Class(object):
    """This class represents a class declared in the module.

    Setting up a class for documentation is easy. You only need to provide an
    object providing 'IModule' as a parent, the name and the klass itself::

      >>> import zope.app.apidoc
      >>> module = Module(None, 'apidoc', zope.app.apidoc)
      >>> klass = Class(module, 'APIDocumentation',
      ...               zope.app.apidoc.APIDocumentation)

    This class provides data about the class in an accessible format. The
    Python path and doc string are easily retrieved using::

      >>> klass.getPath()
      'zope.app.apidoc.APIDocumentation'

      >>> klass.getDocString()[:41]
      'Represent the complete API Documentation.'

    A list of base classes can also be retrieved. The list only includes
    direct bases, so if we have class 'Blah', which extends 'Bar', which
    extends 'Foo', then the bases of 'Blah' is just 'Bar'. In our example this
    looks like this::

      >>> klass.getBases()
      (<class 'zope.app.apidoc.utilities.ReadContainerBase'>,)

    In the other direction, you can get a list of known subclasses.  The list
    only includes those subclasses that are registered with the global
    classRegistry in this module. In our example::

      >>> class APIDocSubclass(zope.app.apidoc.APIDocumentation):
      ...   pass
      >>> klass2 = Class(module, 'APIDocSubclass', APIDocSubclass)
      >>> klass.getKnownSubclasses()
      [<class 'zope.app.apidoc.classmodule.APIDocSubclass'>]

    For a more detailed analysis, you can also retrieve the public attributes
    and methods of this class::

      >>> klass.getAttributes()
      []

      >>> klass.getMethods()[0]
      ('get', <unbound method APIDocumentation.get>, None)

    """
    implements(ILocation, IClassDocumentation)

    def __init__(self, module, name, klass):
        self.__parent__ = module
        self.__name__ = name
        self.__klass = klass

        # Setup interfaces that are implemented by this class.
        self.__interfaces = list(implementedBy(klass))
        all_ifaces = {}
        for iface in self.__interfaces:
            all_ifaces[getPythonPath(iface)] = iface
            for base in [base for base in iface.__bases__]:
                all_ifaces[getPythonPath(base)] = base
        self.__all_ifaces = all_ifaces.values()

        # Register the class with the global class registry.
        global classRegistry
        classRegistry[self.getPath()] = klass

    def getPath(self):
        """See IClassDocumentation."""
        return self.__parent__.getPath() + '.' + self.__name__

    def getDocString(self):
        """See IClassDocumentation."""
        return self.__klass.__doc__

    def getBases(self):
        """See IClassDocumentation."""
        return self.__klass.__bases__

    def getKnownSubclasses(self):
        """See IClassDocumentation."""
        global classRegistry
        return [k for n, k in classRegistry.getSubclassesOf(self.__klass)]

    def getInterfaces(self):
        """See IClassDocumentation."""
        return self.__interfaces

    def getAttributes(self):
        """See IClassDocumentation.

        Here a detailed example::

          >>> from zope.app.apidoc.tests import pprint

          >>> class ModuleStub(object):
          ...      def getPath(self): return ''

          >>> class IBlah(Interface):
          ...      foo = Attribute('Foo')

          >>> class Blah(object):
          ...      implements(IBlah)
          ...      foo = 'f'
          ...      bar = 'b'
          ...      _blah = 'l'

          >>> klass = Class(ModuleStub(), 'Blah', Blah)

          >>> attrs = klass.getAttributes()
          >>> pprint(attrs)
          [('bar', 'b', None),
           ('foo', 'f', <InterfaceClass zope.app.apidoc.classmodule.IBlah>)]
        """
        return [
            (name, getattr(self.__klass, name),
             getInterfaceForAttribute(name, self.__all_ifaces, asPath=False))

            for name in getPublicAttributes(self.__klass)
            if not inspect.ismethod(getattr(self.__klass, name))]

    def getMethods(self):
        """See IClassDocumentation.

        Here a detailed example::

          >>> from zope.app.apidoc.tests import pprint

          >>> class ModuleStub(object):
          ...      def getPath(self): return ''

          >>> class IBlah(Interface):
          ...      def foo(): pass

          >>> class Blah(object):
          ...      implements(IBlah)
          ...      def foo(self): pass
          ...      def bar(self): pass
          ...      def _blah(self): pass

          >>> klass = Class(ModuleStub(), 'Blah', Blah)

          >>> methods = klass.getMethods()
          >>> pprint(methods)
          [('bar', <unbound method Blah.bar>, None),
           ('foo',
            <unbound method Blah.foo>,
            <InterfaceClass zope.app.apidoc.classmodule.IBlah>)]
        """
        return [
            (name, getattr(self.__klass, name),
             getInterfaceForAttribute(name, self.__all_ifaces, asPath=False))

            for name in getPublicAttributes(self.__klass)
            if inspect.ismethod(getattr(self.__klass, name))]

    def getSecurityChecker(self):
        """See IClassDocumentation."""
        return getCheckerForInstancesOf(self.__klass)
