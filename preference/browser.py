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
from zope.security.proxy import removeSecurityProxy
from zope.app.pagetemplate.simpleviewclass import simple
from zope.app.pagetemplate.viewpagetemplatefile import ViewPageTemplateFile
from zope.app.form.browser.editview import EditView

from zope.app.apidoc import utilities


class EditPreferencesGroup(EditView):

    def __init__(self, context, request):
        self.__used_for__ = removeSecurityProxy(context.schema)
        self.schema = removeSecurityProxy(context.schema)
        self.label = context.title + ' Preferences'
        super(EditPreferencesGroup, self).__init__(context, request)

    def getIntroduction(self):
        return utilities.renderText(self.schema.__doc__,
                                    self.schema.__module__)
