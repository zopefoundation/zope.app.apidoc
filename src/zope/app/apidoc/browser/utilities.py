##############################################################################
#
# Copyright (c) 2009 Zope Foundation and Contributors.
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
"""Common Utilities for Browser View

"""
from zope.security.proxy import isinstance
from zope.traversing.api import getParent
from zope.traversing.browser import absoluteURL

from zope.app.apidoc.apidoc import APIDocumentation


def findAPIDocumentationRoot(context, request=None):
    if isinstance(context, APIDocumentation):
        return context
    return findAPIDocumentationRoot(getParent(context), request)


def findAPIDocumentationRootURL(context, request):
    return absoluteURL(findAPIDocumentationRoot(context, request), request)
