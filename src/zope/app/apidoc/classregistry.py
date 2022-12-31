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
"""Class Registry
"""
import operator
import sys

from zope.testing.cleanup import addCleanUp


__docformat__ = 'restructuredtext'

__import_unknown_modules__ = False

# List of modules that should never be imported.
# TODO: List hard-coded for now.
IGNORE_MODULES = ['twisted']


_pathgetter = operator.itemgetter(0)


class ClassRegistry(dict):
    """A simple registry for classes."""

    # This is not a WeakValueDictionary; the classes in here
    # are kept alive almost certainly by the codemodule.class_.Class object,
    # which in turn is kept alive by a codemodule.module.Module chain going
    # all the way back to the APIDocumentation object registered with the
    # global site manager. So they can't go away without clearing all that,
    # which happens (usually only) with test tear downs.

    def getClassesThatImplement(self, iface):
        """Return all class items that implement iface.

        Methods returns a sorted list of 2-tuples of the form (path, class).
        """
        return sorted(((path, klass) for path, klass in self.items()
                       if iface.implementedBy(klass)),
                      key=_pathgetter)

    def getSubclassesOf(self, klass):
        """Return all class items that are proper subclasses of klass.

        Methods returns a sorted list of 2-tuples of the form (path, class).
        """
        return sorted(((path, klass2) for path, klass2 in self.items()
                       if issubclass(klass2, klass) and klass2 is not klass),
                      key=_pathgetter)


#: The global class registry object. Cleaned up
#: in tests by :mod:`zope.testing.cleanup`.
classRegistry = ClassRegistry()


def cleanUp():
    classRegistry.clear()


addCleanUp(cleanUp)


def safe_import(path, default=None):
    """Import a given path as efficiently as possible and without failure."""
    module = sys.modules.get(path, default)
    for exclude_name in IGNORE_MODULES:
        if path.startswith(exclude_name):
            return default
    if module is default and __import_unknown_modules__:
        try:
            module = __import__(path, {}, {}, ('*',))
        # Some software, we cannot control, might raise all sorts of errors;
        # thus catch all exceptions and return the default.
        except Exception:
            return default
    return module
