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
"""Help books.
"""
from zope.testing import cleanup


__docformat__ = 'restructuredtext'
import os.path

from zope.app.onlinehelp.onlinehelp import OnlineHelp
from zope.i18nmessageid import ZopeMessageFactory as _
from zope.interface import implementer

import zope.app.apidoc.bookmodule
from zope.app.apidoc.interfaces import IDocumentationModule


class IBookModule(IDocumentationModule):
    """Interface API Documentation Module

    This is a marker interface, so that we can write adapters for objects
    implementing this interface.
    """


@implementer(IBookModule)
class BookModule(OnlineHelp):
    """Represent a book compiled from various ``README.rst|txt`` and other
    ``*.rst|txt`` documentation files.
    """

    #: Title.
    title = _('Book')

    #: Description.
    description = _("""
    This is a developer's book compiled from all existing documentation
    files. It is not meant to be a complete or cohesive work, but each chapter
    in itself is a little story. Think about it like a collection of fairy
    tales.
    """)

    __parent__ = None
    __name__ = None

    def withParentAndName(self, parent, name):
        located = type(self)(self.title, self.path)
        located.__parent__ = parent
        located.__name__ = name
        return located


# Global Book Instance
path = os.path.join(os.path.dirname(zope.app.apidoc.bookmodule.__file__),
                    'intro.txt')
book = BookModule(_('Book'), path)


def _clear():
    book.__init__(book.title, book.path)


cleanup.addCleanUp(_clear)
