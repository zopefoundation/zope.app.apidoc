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
"""Class Documentation Module

This module is able to take a dotted name of any class and display
documentation for it.

$Id$
"""
__docformat__ = 'restructuredtext'

import os
import sys
import inspect
from types import ClassType, TypeType, FunctionType

import zope
from zope.security.checker import getCheckerForInstancesOf
from zope.interface import Interface, Attribute, implements, implementedBy
from zope.app.container.interfaces import IReadContainer
from zope.app.i18n import ZopeMessageIDFactory as _

from zope.app.location.interfaces import ILocation
from zope.app.apidoc.interfaces import IDocumentationModule
from zope.app.apidoc.utilities import ReadContainerBase
from zope.app.apidoc.utilities import getPythonPath
from zope.app.apidoc.utilities import getPublicAttributes
from zope.app.apidoc.utilities import getInterfaceForAttribute
from zope.app.apidoc.utilities import getFunctionSignature

# Ignore these files, since they are not necessary or cannot be imported
# correctly.
# TODO: I want to be able to specify paths with wildcards later, so that we do
# not ignore all files/dirs with a certain name.
IGNORE_FILES = ('tests', 'tests.py', 'ftests', 'ftests.py', 'CVS', 'gadfly',
                'setup.py', 'introspection.py', 'Mount.py')

class IModuleDocumentation(IReadContainer):
    """Representation of a Python module for documentation.

    The items of the container are sub-modules and classes.
    """
    def getDocString():
        """Return the doc string of the module."""

    def getFileName():
        """Return the file name of the module."""

    def getPath():
        """Return the Python path of the module."""


class IClassDocumentation(Interface):
    """Representation of a class or type for documentation."""

    def getDocString():
        """Return the doc string of the class."""

    def getPath():
        """Return the Python path of the class."""

    def getBases():
        """Return the base classes of the class."""

    def getInterfaces():
        """Return the interfaces the class implements."""

    def getAttributes():
        """Return a list of 3-tuple attribute information.

        The first entry of the 3-tuple is the name of the attribute, the
        second is the attribute object itself. The third entry is the
        interface in which the attribute is defined.

        Note that only public attributes are returned, meaning only attributes
        that do not start with an '_'-character.
        """

    def getMethods():
        """Return a list of 3-tuple method information.

        The first entry of the 3-tuple is the name of the method, the
        second is the method object itself. The third entry is the
        interface in which the method is defined.

        Note that only public methods are returned, meaning only methods
        that do not start with an '_'-character.
        """

    def getSecurityChecker():
        """Return the security checker for this class.

        Since 99% of the time we are dealing with name-based security
        checkers, we can look up the get/set permission required for a
        particular class attribute/method.
        """

class IFunctionDocumentation(Interface):
    """Representation of a function for documentation."""

    def getDocString():
        """Return the doc string of the function."""

    def getPath():
        """Return the Python path of the function."""

    def getSignature():
        """Return the signature of the function as a string."""

    def getAttributes():
        """Return a list of 2-tuple attribute information.

        The first entry of the 2-tuple is the name of the attribute, the
        second is the attribute object itself.
        """

class IZCMLFileDocumentation(Interface):
    """Representation of a function for documentation."""

    path = Attribute('Full path of the ZCML file.')


class Module(ReadContainerBase):
    """This class represents a Python module.

    The module can be easily setup by simply passing the parent module, the
    module name (not the entire Python path) and the Python module instance
    itself::

      >>> import zope.app.apidoc
      >>> module = Module(None, 'apidoc', zope.app.apidoc)

    We can now get some of the common module attributes via accessor methods::

      >>> module.getDocString()[:24]
      'Zope 3 API Documentation'

      >>> fname = module.getFileName()
      >>> fname = fname.replace('\\\\', '/') # normalize pathname separator
      >>> 'zope/app/apidoc/__init__.py' in fname
      True

      >>> module.getPath()
      'zope.app.apidoc'

    The setup for creating the sub module and class tree is automatically
    called during initialization, so that the sub-objects are available as
    soon as you have the object::

      >>> keys = module.keys()
      >>> 'APIDocumentation' in keys
      True
      >>> 'apidocNamespace' in keys
      True
      >>> 'handleNamespace' in keys
      True

      >>> print module['browser'].getPath()
      zope.app.apidoc.browser

    Now, the ``get(key, default=None)`` is actually much smarter than you might
    originally suspect, since it can actually get to more objects than it
    promises. If a key is not found in the module's children, it tries to
    import the key as a module relative to this module.

    For example, while 'tests' directories are not added to the module and
    classes hierarchy (since they do not provide or implement any API), we can
    still get to them::

      >>> print module['tests'].getPath()
      zope.app.apidoc.tests

      >>> names = module['tests'].keys()
      >>> names.sort()
      >>> names
      ['Root', 'pprint', 'rootLocation', 'setUp', 'test_suite']
    """
    implements(ILocation, IModuleDocumentation)

    def __init__(self, parent, name, module, setup=True):
        """Initialize object."""
        self.__parent__ = parent
        self.__name__ = name
        self.__module = module
        self.__children = {}
        if setup:
            self.__setup()

    def __setup(self):
        """Setup the module sub-tree."""
        # Detect packages
        if hasattr(self.__module, '__file__') and \
               (self.__module.__file__.endswith('__init__.py') or
                self.__module.__file__.endswith('__init__.pyc')or
                self.__module.__file__.endswith('__init__.pyo')):
            dir = os.path.split(self.__module.__file__)[0]
            for file in os.listdir(dir):
                if file in IGNORE_FILES:
                    continue
                path = os.path.join(dir, file)

                if os.path.isdir(path) and '__init__.py' in os.listdir(path):
                    fullname = self.__module.__name__ + '.' + file
                    module = safe_import(fullname)
                    if module is not None:
                        self.__children[file] = Module(self, file, module)

                elif os.path.isfile(path) and file.endswith('.py') and \
                         not file.startswith('__init__'):
                    name = file[:-3]
                    fullname = self.__module.__name__ + '.' + name
                    module = safe_import(fullname)
                    if module is not None:
                        self.__children[name] = Module(self, name, module)

                elif os.path.isfile(path) and file.endswith('.zcml'):
                    self.__children[file] = ZCMLFile(self, file, path)

        # Setup classes in module, if any are available.
        for name in self.__module.__dict__.keys():
            attr = getattr(self.__module, name)
            # We do not want to register duplicates or non-"classes"
            if hasattr(attr, '__module__') and \
                   attr.__module__ == self.__module.__name__:

                if type(attr) in (ClassType, TypeType) and \
                       attr.__name__ == name:
                    self.__children[attr.__name__] = Class(self, name, attr)

                elif type(attr) is FunctionType and not name.startswith('_'):
                    self.__children[attr.__name__] = Function(self, name, attr)


    def getDocString(self):
        """See IModule."""
        return self.__module.__doc__

    def getFileName(self):
        """See IModule."""
        return self.__module.__file__

    def getPath(self):
        """See IModule."""
        return self.__module.__name__

    def get(self, key, default=None):
        """See zope.app.container.interfaces.IReadContainer."""
        obj = self.__children.get(key, default)
        if obj is not default:
            return obj

        # We are actually able to find much more than we promise
        if self.getPath():
            path = self.getPath() + '.' + key
        else:
            path = key
        obj = safe_import(path)
        if obj is not None:
            return Module(self, key, obj)

        return default

    def items(self):
        """See zope.app.container.interfaces.IReadContainer."""
        return self.__children.items()


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


class Function(object):
    """This class represents a function declared in the module.

    Setting up a function for documentation is easy. You only need to provide
    an object providing 'IModule' as a parent, the name and the function
    object itself::

      >>> import zope.app.apidoc
      >>> module = Module(None, 'apidoc', zope.app.apidoc)
      >>> func = Function(module, 'handleNamespace',
      ...                 zope.app.apidoc.handleNamespace)

    This class provides data about the function in an accessible format. The
    Python path, signature and doc string are easily retrieved using::

      >>> func.getPath()
      'zope.app.apidoc.handleNamespace'

      >>> func.getSignature()
      '(ob, name)'

      >>> func.getDocString()
      'Used to traverse to an API Documentation.'

    For a more detailed analysis, you can also retrieve the attributes of the
    function::

      >>> func.getAttributes()
      []
    """
    implements(ILocation, IFunctionDocumentation)

    def __init__(self, module, name, func):
        self.__parent__ = module
        self.__name__ = name
        self.__func = func

    def getPath(self):
        """See IFunctionDocumentation."""
        return self.__parent__.getPath() + '.' + self.__name__

    def getDocString(self):
        """See IFunctionDocumentation."""
        return self.__func.__doc__

    def getSignature(self):
        """See IFunctionDocumentation."""
        return getFunctionSignature(self.__func)

    def getAttributes(self):
        """See IClassDocumentation.

        Here a detailed example::

          >>> class ModuleStub(object):
          ...      def getPath(self): return ''

          >>> def foo(bar=1):
          ...     pass

          >>> func = Function(ModuleStub(), 'foo', foo)

          >>> attrs = func.getAttributes()
          >>> attrs.sort()
          >>> print attrs
          []

          >>> foo.bar = 'blah'
          >>> attrs = func.getAttributes()
          >>> attrs.sort()
          >>> print attrs
          [('bar', 'blah')]
        """
        return self.__func.__dict__.items()


class ZCMLFile(object):
    """Represent the documentation of any ZCML file.

    This object in itself is rather simple, since it only stores the full path
    of the ZCML file and its location in the documentation tree.

    >>> zcml = ZCMLFile(None, 'foo.zcml', '/Zope3/src/zope/app/foo.zcml')
    >>> zcml.__parent__ is None
    True
    >>> zcml.__name__
    'foo.zcml'
    >>> zcml.path
    '/Zope3/src/zope/app/foo.zcml'
    """
    
    implements(ILocation, IZCMLFileDocumentation)

    def __init__(self, module, name, path):
        """Initialize the object."""
        self.__parent__ = module
        self.__name__ = name
        self.path = path


class ClassModule(Module):
    """Represent the Documentation of any possible class.

    This object extends a module, since it can be seen as some sort of root
    module. However, its sementacs are obviously a bit different::

      >>> cm = ClassModule()

      >>> cm.getDocString()
      u'Zope 3 root.'
      >>> cm.getFileName()
      ''
      >>> cm.getPath()
      ''

      >>> names = cm.keys()
      >>> names.sort()
      >>> names == cm.rootModules
      True
    """
    implements(IDocumentationModule)

    # See zope.app.apidoc.interfaces.IDocumentationModule
    title = _('Classes')

    # See zope.app.apidoc.interfaces.IDocumentationModule
    description = _("""
    This module allows you to get an overview of the modules and classes
    defined in the Zope 3 framework and its supporting packages. There are
    two methods to navigate through the modules to find the classes you are
    interested in.

    The first method is to type in some part of the Python path of the class
    and the module will look in the class registry for matches. The menu will
    then return with a list of these matches.

    The second method is to click on the "Browse Zope Source" link. In the
    main window, you will see a directory listing with the root Zope 3
    modules. You can click on the module names to discover their content. If a
    class is found, it is represented as a bold entry in the list.

    The documentation contents of a class provides you with an incredible
    amount of information. Not only does it tell you about its base classes,
    implemented interfaces, attributes and methods, but it also lists the
    interface that requires a method or attribute to be implemented and the
    permissions required to access it.
    """)
    rootModules = ['ZConfig', 'ZODB', 'transaction', 'zdaemon', 'zope']

    def __init__(self):
        """Initialize object."""
        super(ClassModule, self).__init__(None, '', None, False)
        self.__isSetup = False

    def __setup(self):
        """Setup module and class tree."""
        for name in self.rootModules:
            self._Module__children[name] = Module(self, name, safe_import(name))

    def getDocString(self):
        """See Module class."""
        return _('Zope 3 root.')

    def getFileName(self):
        """See Module class."""
        return ''

    def getPath(self):
        """See Module class."""
        return ''

    def get(self, key, default=None):
        """See zope.app.container.interfaces.IReadContainer."""
        if self.__isSetup is False:
            self.__setup()
            self.__isSetup = True
        return super(ClassModule, self).get(key, default)

    def items(self):
        """See zope.app.container.interfaces.IReadContainer."""
        if self.__isSetup is False:
            self.__setup()
            self.__isSetup = True
        return super(ClassModule, self).items()


class ClassRegistry(dict):
    """A simple registry for classes.

    This little registry allows us to quickly query a complete list of classes
    that are defined and used by Zope 3. The prime feature of the class is the
    'getClassesThatImplement(iface)' method that returns all classes that
    implement the passed interface.

    Here is the registry in action::

      >>> reg = ClassRegistry()

      >>> class IA(Interface):
      ...      pass
      >>> class IB(IA):
      ...      pass
      >>> class IC(Interface):
      ...      pass
      >>> class ID(Interface):
      ...      pass

      >>> class A(object):
      ...    implements(IA)
      >>> reg['A'] = A
      >>> class B:
      ...    implements(IB)
      >>> reg['B'] = B
      >>> class B2(object):
      ...    implements(IB)
      >>> reg['B2'] = B2
      >>> class C(object):
      ...    implements(IC)
      >>> reg['C'] = C

      >>> names = reg.keys()
      >>> names.sort()
      >>> names
      ['A', 'B', 'B2', 'C']

      >>> reg['A'] is A
      True

      >>> [n for n, k in reg.getClassesThatImplement(IA)]
      ['A', 'B', 'B2']
      >>> [n for n, k in reg.getClassesThatImplement(IB)]
      ['B', 'B2']
      >>> [n for n, k in reg.getClassesThatImplement(IC)]
      ['C']
      >>> [n for n, k in reg.getClassesThatImplement(ID)]
      []
    """

    def getClassesThatImplement(self, iface):
        """Return the all class items that implement iface.

        Methods returns a 2-tuple of the form (path, class).
        """
        return [(path, klass) for path, klass in self.items()
                if iface.implementedBy(klass)]


classRegistry = ClassRegistry()

def cleanUp():
    classRegistry.clear()

from zope.testing.cleanup import addCleanUp
addCleanUp(cleanUp)


def safe_import(path, default=None):
    r"""Import a given path as efficiently as possible and without failure.

    First we try to find the path in 'sys.modules', since this lookup is much
    more efficient than importing it. If it was not found, we go back and try
    to import the path. If that also fails, we return the 'default' value.

    Here are some examples::

      >>> 'zope.app' in sys.modules
      True
      >>> safe_import('zope.app') is sys.modules['zope.app']
      True

      >>> safe_import('weirdname') is None
      True

    For this example, we'll create a dummy module:

      >>> here = os.path.dirname(__file__)
      >>> filename = os.path.join(here, 'testmodule.py')
      >>> f = open(filename, 'w')
      >>> f.write('# dummy module\n')
      >>> f.close()

    The temporary module is not already imported, but will be once
    we've called safe_import():

      >>> module_name = __name__ + '.testmodule'
      >>> module_name in sys.modules
      False
      >>> safe_import(module_name).__name__ == module_name
      True
      >>> module_name in sys.modules
      True
      >>> del sys.modules[module_name]

    Now clean up the temporary module, just to play nice:

      >>> os.unlink(filename)
      >>> if os.path.exists(filename + 'c'):
      ...     os.unlink(filename + 'c')
      >>> if os.path.exists(filename + 'o'):
      ...     os.unlink(filename + 'o')
    """
    module = sys.modules.get(path, default)
    if module is default:
        try:
            module = __import__(path, {}, {}, ('*',))
        except ImportError:
            return default
    return module
