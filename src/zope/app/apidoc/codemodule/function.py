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
"""Function representation for code browser

"""
__docformat__ = 'restructuredtext'

from zope.interface import implementer
from zope.location.interfaces import ILocation

from zope.app.apidoc.utilities import getFunctionSignature
from zope.app.apidoc.codemodule.interfaces import IFunctionDocumentation


@implementer(ILocation, IFunctionDocumentation)
class Function(object):
    """This class represents a function declared in the module."""

    def __init__(self, module, name, func, doc=None):
        self.__parent__ = module
        self.__name__ = name
        self.__func = func
        if doc is None:
            self.__doc__ = func.__doc__
        else:
            self.__doc__ = doc

    def getPath(self):
        """See :class:`~zope.app.apidoc.codemodule.interfaces.IFunctionDocumentation`."""
        return self.__parent__.getPath() + '.' + self.__name__

    def getDocString(self):
        """See :class:`~zope.app.apidoc.codemodule.interfaces.IFunctionDocumentation`."""
        return self.__doc__

    def getSignature(self):
        """See :class:`~zope.app.apidoc.codemodule.interfaces.IFunctionDocumentation`."""
        return getFunctionSignature(self.__func)

    def getAttributes(self):
        """See :class:`~zope.app.apidoc.codemodule.interfaces.IFunctionDocumentation`."""
        return list(self.__func.__dict__.items())
