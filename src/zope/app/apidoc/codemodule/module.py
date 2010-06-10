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
"""Module representation for code browser

$Id$
"""
__docformat__ = 'restructuredtext'
import os
import types

import zope
from zope.interface import implements
from zope.interface import providedBy
from zope.interface.interface import InterfaceClass
from zope.location.interfaces import ILocation
from zope.location import LocationProxy
from zope.hookable import hookable

from zope.app.apidoc.classregistry import safe_import
from zope.app.apidoc.utilities import ReadContainerBase
from interfaces import IModuleDocumentation

from zope.app.apidoc.codemodule.class_ import Class
from zope.app.apidoc.codemodule.function import Function
from zope.app.apidoc.codemodule.text import TextFile
from zope.app.apidoc.codemodule.zcml import ZCMLFile

# Ignore these files, since they are not necessary or cannot be imported
# correctly.
IGNORE_FILES = ('tests', 'tests.py', 'ftests', 'ftests.py', 'CVS', 'gadfly',
                'setup.py', 'introspection.py', 'Mount.py')

class Module(ReadContainerBase):
    """This class represents a Python module."""
    implements(ILocation, IModuleDocumentation)

    def __init__(self, parent, name, module, setup=True):
        """Initialize object."""
        self.__parent__ = parent
        self.__name__ = name
        self._module = module
        self._children = {}
        self._package = False
        if setup:
            self.__setup()

    def __setup(self):
        """Setup the module sub-tree."""
        # Detect packages
        if hasattr(self._module, '__file__') and \
               (self._module.__file__.endswith('__init__.py') or
                self._module.__file__.endswith('__init__.pyc')or
                self._module.__file__.endswith('__init__.pyo')):
            self._package = True
            for dir in self._module.__path__:
                # TODO: If we are dealing with eggs, we will not have a
                # directory right away. For now we just ignore zipped eggs;
                # later we want to unzip it.
                if not os.path.isdir(dir):
                    continue
                for file in os.listdir(dir):
                    if file in IGNORE_FILES or file in self._children:
                        continue
                    path = os.path.join(dir, file)

                    if (os.path.isdir(path) and
                        '__init__.py' in os.listdir(path)):
                        # subpackage
                        fullname = self._module.__name__ + '.' + file
                        module = safe_import(fullname)
                        if module is not None:
                            self._children[file] = Module(self, file, module)

                    elif os.path.isfile(path) and file.endswith('.py') and \
                             not file.startswith('__init__'):
                        # module
                        name = file[:-3]
                        fullname = self._module.__name__ + '.' + name
                        module = safe_import(fullname)
                        if module is not None:
                            self._children[name] = Module(self, name, module)

                    elif os.path.isfile(path) and file.endswith('.zcml'):
                        self._children[file] = ZCMLFile(path, self._module,
                                                        self, file)

                    elif os.path.isfile(path) and file.endswith('.txt'):
                        self._children[file] = TextFile(path, file, self)

        # List the classes and functions in module, if any are available.
        zope.deprecation.__show__.off()
        module_decl = self.getDeclaration()
        ifaces = list(module_decl)
        if ifaces:
            # The module has an interface declaration.  Yay!
            names = set()
            for iface in ifaces:
                names.update(iface.names())
        else:
            names = getattr(self._module, '__all__', None)
            if names is None:
                # The module doesn't declare its interface.  Boo!
                # Guess what names to document, avoiding aliases and names
                # imported from other modules.
                names = []
                for name in self._module.__dict__.keys():
                    attr = getattr(self._module, name, None)
                    attr_module = getattr(attr, '__module__', None)
                    if attr_module != self._module.__name__:
                        continue
                    if getattr(attr, '__name__', None) != name:
                        continue
                    names.append(name)

        for name in names:
            # If there is something the same name beneath, then module should
            # have priority.
            if name in self._children:
                continue

            attr = getattr(self._module, name, None)
            if attr is None:
                continue

	    if isinstance(attr, hookable):
		attr = attr.implementation

            if isinstance(attr, (types.ClassType, types.TypeType)):
                self._children[name] = Class(self, name, attr)

            elif isinstance(attr, InterfaceClass):
                self._children[name] = LocationProxy(attr, self, name)

            elif isinstance(attr, types.FunctionType):
                doc = attr.__doc__
                if not doc:
                    f = module_decl.get(name)
                    if f is not None:
                        doc = f.__doc__
                self._children[name] = Function(self, name, attr, doc=doc)

        zope.deprecation.__show__.on()


    def getDocString(self):
        """See IModuleDocumentation."""
        return self._module.__doc__

    def getFileName(self):
        """See IModuleDocumentation."""
        return self._module.__file__

    def getPath(self):
        """See IModuleDocumentation."""
        return self._module.__name__

    def isPackage(self):
        """See IModuleDocumentation."""
        return self._package

    def getDeclaration(self):
        """See IModuleDocumentation."""
        return providedBy(self._module)

    def get(self, key, default=None):
        """See zope.container.interfaces.IReadContainer."""
        obj = self._children.get(key, default)
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

        # Maybe it is a simple attribute of the module
        if obj is None:
            obj = getattr(self._module, key, default)
            if obj is not default:
                obj = LocationProxy(obj, self, key)

        return obj

    def items(self):
        """See zope.container.interfaces.IReadContainer."""
        # Only publicize public objects, even though we do keep track of
        # private ones
        return [(name, value)
                for name, value in self._children.items()
                if not name.startswith('_')]
