##############################################################################
#
# Copyright (c) 2005 Zope Corporation and Contributors.
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
"""API Doc Preference Views

$Id$
"""
__docformat__ = "reStructuredText"

from zope.app import zapi
from zope.app.tree.browser.cookie import CookieTreeView
from zope.app.preference.browser import PreferenceGroupFilter

class APIDocPreferencesTree(CookieTreeView):
    """Preferences Tree using the stateful cookie tree."""

    def apidocTree(self):
        root = zapi.getRoot(self.context)['apidoc']
        filter = PreferenceGroupFilter()
        return self.cookieTree(root, filter)


