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
"""This module handles the 'apidoc:rootModule' and 'apidoc:moduleImport'
 namespace directives.

"""
__docformat__ = 'restructuredtext'
from zope.component.zcml import utility
from zope.interface import implementer

from zope.app.apidoc import classregistry
from zope.app.apidoc.codemodule.interfaces import IAPIDocRootModule


@implementer(IAPIDocRootModule)
class RootModule(str):
    pass


def rootModule(_context, module):
    """Register a new module as a root module for the class browser."""
    utility(_context, IAPIDocRootModule, RootModule(module), name=module)


def setModuleImport(flag):
    classregistry.__import_unknown_modules__ = flag


def moduleImport(_context, allow):
    """Set the __import_unknown_modules__ flag"""
    return _context.action(
        ('apidoc', '__import_unknown_modules__'),
        setModuleImport,
        (allow, ))
