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
"""Main API Documentation View

"""
__docformat__ = 'restructuredtext'

from zope.i18n import translate
from zope.security.proxy import removeSecurityProxy

from zope.app.apidoc.utilities import renderText


class APIDocumentationView:
    """View for the API Documentation"""

    context = None
    request = None

    def getModuleList(self):
        """Get a list of all available documentation modules."""
        items = sorted(self.context.items())
        result = []
        for name, module in items:
            description = removeSecurityProxy(module.description)
            description = translate(description, context=self.request,
                                    default=description)
            description = renderText(description, module.__class__.__module__)
            assert not isinstance(description, bytes)
            result.append({'name': name,
                           'title': module.title,
                           'description': description})
        return result
