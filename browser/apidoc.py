##############################################################################
#
# Copyright (c) 2004 Zope Corporation and Contributors.
# All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.0 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
##############################################################################
"""Main API Documentation View

$Id: apidoc.py,v 1.2 2004/03/10 12:24:16 srichter Exp $
"""
from zope.app.apidoc.utilities import stx2html

class APIDocumentation(object):
    """View for the API Documentation"""

    def getModuleList(self):
        """Get a list of all available documentation modules."""
        items = list(self.context.items())
        items.sort()
        return [{'name': name,
                 'title': module.title,
                 'description': stx2html(module.description)}
                for name, module in items ]
