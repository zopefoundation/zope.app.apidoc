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
"""Function Views

$Id: browser.py 29143 2005-02-14 22:43:16Z srichter $
"""
__docformat__ = 'restructuredtext'
from zope.app import zapi
from zope.app.apidoc.utilities import getPythonPath, renderText

class FunctionDetails(object):
    """Represents the details of the function."""

    def getDocString(self):
        """Get the doc string of the function in a rendered format."""
        return renderText(self.context.getDocString() or '',
                          zapi.getParent(self.context).getPath())


    def getAttributes(self):
        """Get all attributes of this function."""
        return [{'name': name,
                 'value': `attr`,
                 'type': type(attr).__name__,
                 'type_link': getPythonPath(type(attr)).replace('.', '/')}
                
                for name, attr in self.context.getAttributes()]
