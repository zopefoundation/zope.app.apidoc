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

from zope.app.apidoc.codemodule.interfaces import ITextFile


@implementer(ILocation, ITextFile)
class TextFile(object):
    """This class represents a function declared in the module."""

    def __init__(self, path, name, package):
        self.path = path
        self.__parent__ = package
        self.__name__ = name

    def getContent(self):
        with open(self.path, 'rb') as f:
            content = f.read()

        # Make newlines universal
        content = content.replace(b'\r\n', b'\n')
        content = content.replace(b'\r', b'\n')

        return content.decode('utf-8')
