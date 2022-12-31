##############################################################################
#
# Copyright (c) 2001, 2002 Zope Foundation and Contributors.
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
"""Schema for the ``apidoc:bookchapter`` directive

"""
__docformat__ = 'restructuredtext'

from zope.configuration.fields import MessageID
from zope.configuration.fields import Path
from zope.configuration.fields import Tokens
from zope.interface import Interface
from zope.schema import NativeStringLine
from zope.schema import TextLine


class IBookChapterDirective(Interface):
    """Register a new Book Chapter"""

    id = NativeStringLine(
        title="Topic Id",
        description="Id of the chapter as it will appear in the URL.",
        required=True)

    title = MessageID(
        title="Title",
        description="Provides a title for the chapter.",
        required=True)

    doc_path = Path(
        title="Path to File",
        description="Path to the file that contains the chapter content.",
        required=False)

    parent = NativeStringLine(
        title="Parent Chapter",
        description="Id of the parent chapter.",
        default="",
        required=False)

    resources = Tokens(
        title="A list of resources.",
        description="""
        A list of resources which shall be user for the chapter. The
        resources must be located in the same directory as the chapter.
        """,
        value_type=TextLine(),
        required=False
    )
