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

"""
__docformat__ = 'restructuredtext'
import os
import types

import six

from zope.cachedescriptors.property import Lazy
from zope.hookable import hookable
from zope.interface import implementer
from zope.interface import providedBy
from zope.interface.interface import InterfaceClass
from zope.location import LocationProxy
from zope.location.interfaces import ILocation
from zope.proxy import getProxiedObject

import zope
from zope.app.apidoc.classregistry import safe_import
from zope.app.apidoc.codemodule.class_ import Class
from zope.app.apidoc.codemodule.function import Function
from zope.app.apidoc.codemodule.interfaces import IModuleDocumentation
from zope.app.apidoc.codemodule.text import TextFile
from zope.app.apidoc.codemodule.zcml import ZCMLFile
from zope.app.apidoc.utilities import ReadContainerBase


# Ignore these files, since they are not necessary or cannot be imported
# correctly.
IGNORE_FILES = frozenset((
    'tests',
    'tests.py',
    'ftests',
    'ftests.py',
    'CVS',
    '.svn',
    '.git',
    'gadfly',
    'setup.py',
    'introspection.py',
    'Mount.py',
    '__main__.py',
))


@implementer(ILocation, IModuleDocumentation)
class Module(ReadContainerBase):
    """This class represents a Python module."""

    _package = False
    _children = None

    def __init__(self, parent, name, module, setup=True):
        """Initialize object."""
        self.__parent__ = parent
        self.__name__ = name
        self._module = module
        self._children = {}
        if setup:
            self.__setup()

    def __setup_package(self):
        # Detect packages
        # __file__ can be None, especially with namespace packages on
        # Python 3.7
        module_file = getattr(self._module, '__file__', None) or ''
        module_path = getattr(self._module, '__path__', None)
        if module_file.endswith(
                ('__init__.py', '__init__.pyc', '__init__.pyo')):
            self._package = True
        elif hasattr(self._module, '__package__'):
            # Detect namespace packages, especially (but not limited
            # to) Python 3 with implicit namespace packages:

            # "When the module is a package, its
            # __package__ value should be set to its __name__. When
            # the module is not a package, __package__ should be set
            # to the empty string for top-level modules, or for
            # submodules, to the parent package's "

            # Note that everything has __package__ on Python 3, but not
            # necessarily on Python 2.
            pkg_name = self._module.__package__
            self._package = pkg_name and self._module.__name__ == pkg_name
        else:
            # Python 2. Lets do some introspection. Namespace packages
            # often have an empty file. Note that path isn't necessarily
            # indexable.
            if (module_file == ''
                and module_path
                    and os.path.isdir(list(module_path)[0])):
                self._package = True

        if not self._package:
            return

        for mod_dir in module_path:
            # TODO: If we are dealing with eggs, we will not have a
            # directory right away. For now we just ignore zipped eggs;
            # later we want to unzip it.
            if not os.path.isdir(mod_dir):
                continue

            for mod_file in os.listdir(mod_dir):
                if mod_file in IGNORE_FILES or mod_file in self._children:
                    continue

                path = os.path.join(mod_dir, mod_file)

                if os.path.isdir(path) and '__init__.py' in os.listdir(path):
                    # subpackage
                    # XXX Python 3 implicit packages don't have __init__.py

                    fullname = self._module.__name__ + '.' + mod_file
                    module = safe_import(fullname)
                    if module is not None:
                        self._children[mod_file] = Module(
                            self, mod_file, module)
                elif os.path.isfile(path):
                    if mod_file.endswith(
                            '.py') and not mod_file.startswith('__init__'):
                        # module
                        name = mod_file[:-3]
                        fullname = self._module.__name__ + '.' + name
                        module = safe_import(fullname)
                        if module is not None:
                            self._children[name] = Module(self, name, module)

                    elif mod_file.endswith('.zcml'):
                        self._children[mod_file] = ZCMLFile(path, self._module,
                                                            self, mod_file)

                    elif mod_file.endswith(('.txt', '.rst')):
                        self._children[mod_file] = TextFile(
                            path, mod_file, self)

    def __setup_classes_and_functions(self):
        # List the classes and functions in module, if any are available.
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
                names = set()
                for name, attr in self._module.__dict__.items():
                    if isinstance(attr, hookable):
                        attr = attr.implementation
                    attr_module = getattr(attr, '__module__', None)
                    if attr_module != self._module.__name__:
                        continue
                    if getattr(attr, '__name__', None) != name:
                        continue
                    names.add(name)

        # If there is something the same name beneath, then module should
        # have priority.
        names = set(names) - set(self._children)

        for name in names:
            attr = getattr(self._module, name, None)
            if attr is None:
                continue

            if isinstance(attr, hookable):
                attr = attr.implementation

            if isinstance(attr, six.class_types):
                self._children[name] = Class(self, name, attr)

            elif isinstance(attr, InterfaceClass):
                self._children[name] = LocationProxy(attr, self, name)

            elif isinstance(attr, types.FunctionType):
                doc = attr.__doc__
                if not doc:
                    f = module_decl.get(name)
                    doc = getattr(f, '__doc__', None)
                self._children[name] = Function(self, name, attr, doc=doc)

    def __setup(self):
        """Setup the module sub-tree."""
        self.__setup_package()

        zope.deprecation.__show__.off()
        try:
            self.__setup_classes_and_functions()
        finally:
            zope.deprecation.__show__.on()

    def withParentAndName(self, parent, name):
        located = _LazyModule(self, parent, name, self._module)
        # Our module tree can be very large, but typically during any one
        # traversal we're only going to need one specific branch. So
        # initializing it lazily the first time one specific level's _children
        # is accessed has a *major* performance benefit.
        # A plain @Lazy attribute won't work since we need to copy from self;
        # we use a subclass, with the provisio that it can be the *only*
        # subclass
        return located

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

        if self.getPath():
            # Look for a nested module we didn't previously discover.

            # Note that when path is empty, that means we are the global
            # module (CodeModule) and if we get here, we're asking to find
            # a module outside of the registered root modules. We don't
            # look for those things.

            # A common case for this to come up is 'menus' for the 'zope.app'
            # module. The 'menus' module is dynamically generated through ZCML.

            path = self.getPath() + '.' + key

            obj = safe_import(path)

            if obj is not None:
                self._children[key] = child = Module(self, key, obj)
                # Caching this in _children may be pointless, we were
                # most likely a copy using withParentAndName in the
                # first place.
                return child

        # Maybe it is a simple attribute of the module
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

    def __repr__(self):
        return '<Module %r name %r parent %r at 0x%x>' % (
            self._module, self.__name__, self.__parent__, id(self)
        )


class _LazyModule(Module):

    copy_from = None

    def __init__(self, copy_from, parent, name, module):
        Module.__init__(self, parent, name, module, False)
        del self._children  # get our @Lazy back
        self._copy_from = copy_from

    @Lazy
    def _children(self):
        new_children = {}
        for x in self._copy_from._children.values():
            try:
                new_child = x.withParentAndName(self, x.__name__)
            except AttributeError:
                if isinstance(x, LocationProxy):
                    new_child = LocationProxy(
                        getProxiedObject(x), self, x.__name__)
                else:
                    new_child = LocationProxy(x, self, x.__name__)

            new_children[x.__name__] = new_child
        return new_children
