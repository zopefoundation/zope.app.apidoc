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
"""Generic API Documentation Interfaces
"""
__docformat__ = 'restructuredtext'


from zope.location.interfaces import ILocation
from zope.schema import Text
from zope.schema import TextLine


class IDocumentationModule(ILocation):
    """Zope 3 API Documentation Module

    A documentation module contains the documentation for one specific aspect
    of the framework, such as ZCML directives or interfaces.

    The interface is used to register module as utilities.
    """

    title = TextLine(
        title=u"Title",
        description=u"The title of the documentation module.",
        required=True)

    description = Text(
        title=u"Module Description",
        description=u"This text describes the functionality of the module.",
        required=True)

    def withParentAndName(parent, name):
        """
        Return a new object that is a copy of this object, but
        being located at the given parent and name.
        """
