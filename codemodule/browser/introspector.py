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
"""Introspector view for content components

$Id: browser.py 29143 2005-02-14 22:43:16Z srichter $
"""
__docformat__ = 'restructuredtext'
from zope.security.proxy import removeSecurityProxy
from zope.app.publisher.browser import BrowserView


class Introspector(BrowserView):

    def __call__(self):
        klass = type(removeSecurityProxy(self.context))
        url = self.request.getApplicationURL() + '/++apidoc++/Code/'
        url += klass.__module__.replace('.', '/') + '/'
        url += klass.__name__ + '/index.html'
        self.request.response.redirect(url)
