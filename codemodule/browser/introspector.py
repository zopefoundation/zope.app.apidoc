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

import zope.interface

from zope.security.proxy import removeSecurityProxy
from zope.app.container.contained import getProxiedObject
from zope.app.publisher.browser import BrowserView


class Introspector(BrowserView):

    def get_object(self):
        return getProxiedObject(removeSecurityProxy(self.context))

    def class_name(self):
        klass = type(self.get_object())
        return "%s.%s" % (klass.__module__, klass.__name__)

    def class_url(self):
        klass = type(self.get_object())
        url = self.request.getApplicationURL() + '/++apidoc++/Code/'
        url += klass.__module__.replace('.', '/') + '/'
        return url + klass.__name__ + '/index.html'

    def direct_interfaces(self):
        ifaces = zope.interface.directlyProvidedBy(self.get_object())
        result = []
        urlbase = self.request.getApplicationURL() + '/++apidoc++/Interface/'
        for iface in ifaces:
            url = "%s%s.%s/apiindex.html" % (
                urlbase, iface.__module__, iface.__name__)
            result.append(("%s.%s" % (iface.__module__, iface.__name__),
                           {"name": iface.__name__,
                            "module": iface.__module__,
                            "url": url}))
        result.sort()
        return [dict for name, dict in result]
