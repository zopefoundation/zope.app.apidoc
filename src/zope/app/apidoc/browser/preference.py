##############################################################################
#
# Copyright (c) 2005 Zope Foundation and Contributors.
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

"""
__docformat__ = "reStructuredText"

from zope.app.preference.browser import EditPreferenceGroup
from zope.app.preference.browser import PreferenceGroupFilter
from zope.app.tree.browser.cookie import CookieTreeView
from zope.publisher.browser import applySkin
from zope.traversing.api import getRoot

from zope.app.apidoc.browser.skin import APIDOC


class APIDocPreferencesTree(CookieTreeView):
    """Preferences Tree using the stateful cookie tree."""

    def apidocTree(self):
        root = getRoot(self.context)['apidoc']
        return self.cookieTree(root, PreferenceGroupFilter())


class ApidocEditPreferenceGroup(EditPreferenceGroup):

    def __init__(self, context, request):
        # Make sure we enter APIDOC territory.
        applySkin(request, APIDOC)
        super(ApidocEditPreferenceGroup, self).__init__(context, request)
