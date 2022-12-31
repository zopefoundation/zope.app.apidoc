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
"""Function Views

"""
__docformat__ = 'restructuredtext'
from zope.app.apidoc.utilities import renderText


class TextFileDetails:
    """Represents the details of the text file."""

    context = None
    request = None

    def renderedContent(self):
        """Render the file content to HTML."""
        ctx = self.context
        format = 'zope.source.stx' if ctx.path.endswith(
            '.stx') else 'zope.source.rest'
        return renderText(ctx.getContent(), format=format)
