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
"""User Preferences Browser Views

$Id: menu.py 29269 2005-02-23 22:22:48Z srichter $
"""
__docformat__ = 'restructuredtext'
import re
import zope.interface
import zope.schema
from zope.security.proxy import removeSecurityProxy

from zope.app import zapi
from zope.app.basicskin.standardmacros import StandardMacros
from zope.app.container.interfaces import IObjectFindFilter
from zope.app.form.browser.editview import EditView
from zope.app.pagetemplate.simpleviewclass import simple
from zope.app.pagetemplate.viewpagetemplatefile import ViewPageTemplateFile
from zope.app.tree.browser.cookie import CookieTreeView

from zope.app.apidoc.preference import interfaces

NoneInterface = zope.interface.interface.InterfaceClass('None')

class PreferencesMacros(StandardMacros):
    """Page Template METAL macros for preferences"""
    macro_pages = ('preference_macro_definitions',)


class PreferenceGroupFilter(object):
    """A special filter for """
    zope.interface.implements(IObjectFindFilter)

    def matches(self, obj):
        """Decide whether the object is shown in the tree."""
        if interfaces.IPreferenceCategory.providedBy(obj):
            return True

        if interfaces.IPreferenceGroup.providedBy(obj):
            parent = zapi.getParent(obj)
            if interfaces.IPreferenceCategory.providedBy(parent):
                return True

        return False
        

class PreferencesTree(CookieTreeView):
    """Preferences Tree using the stateful cookie tree."""

    def tree(self):
        root = zapi.getRoot(self.context)
        filter = PreferenceGroupFilter()
        return self.cookieTree(root, filter)


class EditPreferenceGroup(EditView):

    def __init__(self, context, request):
        self.__used_for__ = removeSecurityProxy(context.schema)
        self.schema = removeSecurityProxy(context.schema)

        if self.schema is None:
            self.schema = NoneInterface 
            zope.interface.alsoProvides(removeSecurityProxy(context),
                                        NoneInterface)
            
        self.label = context.title + ' Preferences'
        super(EditPreferenceGroup, self).__init__(context, request)
        self.setPrefix(context.id)

    def getIntroduction(self):
        # TODO: Remove dependency
        from zope.app.apidoc import utilities
        text = self.context.description or self.schema.__doc__

        # Determine common whitespace ...
        cols = len(re.match('^[ ]*', text).group())
        # ... and clean it up.
        text = re.sub('\n[ ]{%i}' %cols, '\n', text)

        return utilities.renderText(text.strip(), self.schema.__module__)

