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

$Id: apidoc.py,v 1.1 2004/02/19 20:46:39 philikon Exp $
"""
from zope.app.apidoc.utilities import stx2html

__metaclass__ = type

class APIDocumentation:
    """View for the API Documentation"""

    def getModuleList(self):
        """Get a list of all available documentation modules."""
        modules = []
        items = list(self.context.items())
        items.sort()
        return [{'name': name,
                 'title': m.title,
                 'description': stx2html(m.description)}
                for name, m in items ]
