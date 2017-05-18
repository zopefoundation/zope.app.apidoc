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

from zope.traversing.api import getParent, traverse
from zope.traversing.browser import absoluteURL


from zope.app.apidoc.utilities import renderText

from zope.app.apidoc.codemodule.browser.class_ import getTypeLink

class FunctionDetails(object):
    """Represents the details of the function."""

    context = None
    request = None

    def getDocString(self):
        """Get the doc string of the function in a rendered format."""
        return renderText(self.context.getDocString() or '',
                          getParent(self.context).getPath())


    def getAttributes(self):
        """Get all attributes of this function."""
        return [{'name': name,
                 'value': repr(attr),
                 'type': type(attr).__name__,
                 'type_link': getTypeLink(type(attr))}

                for name, attr in self.context.getAttributes()]


    def getBaseURL(self):
        """Return the URL for the API Documentation Tool."""
        apidoc = traverse(self.context, '/++apidoc++')
        m = apidoc['Code']
        return absoluteURL(getParent(m), self.request)
