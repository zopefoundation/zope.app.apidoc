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
"""This module handles the 'apidoc' namespace directives.

$Id: metaconfigure.py 26889 2004-08-04 04:00:36Z pruggera $
"""
__docformat__ = 'restructuredtext'
from zope.interface import implements
from zope.app.component.metaconfigure import utility
from zope.app.apidoc.codemodule.interfaces import IAPIDocRootModule

class RootModule(str):
    implements(IAPIDocRootModule)

def rootModule(_context, module):
    """Register a new module as a root module for the class browser."""
    utility(_context, IAPIDocRootModule, RootModule(module), name=module)
