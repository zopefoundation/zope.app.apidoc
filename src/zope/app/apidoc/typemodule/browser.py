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
"""Browser Views for Interface Types

"""
__docformat__ = 'restructuredtext'
from zope.security.proxy import isinstance
from zope.security.proxy import removeSecurityProxy
from zope.traversing.api import getName

from zope.app.apidoc.browser.utilities import findAPIDocumentationRootURL
from zope.app.apidoc.typemodule.type import TypeInterface


class Menu:
    """Menu View Helper Class"""

    context = None
    request = None

    def getMenuTitle(self, node):
        """Return the title of the node that is displayed in the menu."""
        if isinstance(node.context, TypeInterface):
            iface = node.context.interface
        else:
            iface = node.context
        # Interfaces have no security declarations, so we have to unwrap.
        return removeSecurityProxy(iface).getName()

    def getMenuLink(self, node):
        """Return the HTML link of the node that is displayed in the menu."""
        root_url = findAPIDocumentationRootURL(self.context, self.request)
        return '{}/Interface/{}/index.html'.format(
            root_url, getName(node.context))
