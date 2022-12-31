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
"""Stubs for when documentation is disabled.

"""
__docformat__ = 'restructuredtext'


class APIDocStub:
    """A stub to use as display context when APIDoc is disabled.
    """


class apidocNamespace:
    """Used to traverse to an API Documentation when it is disabled."""

    def __init__(self, ob, request=None):
        self.request = request
        self.context = ob

    def traverse(self, name, ignore):
        return APIDocStub()
