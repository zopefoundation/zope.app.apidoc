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
"""Module Views

$Id: browser.py 29143 2005-02-14 22:43:16Z srichter $
"""
__docformat__ = 'restructuredtext'
from zope.interface.interface import InterfaceClass
from zope.security.proxy import removeSecurityProxy
from zope.proxy import removeAllProxies

from zope.app import zapi
from zope.app.i18n import ZopeMessageIDFactory as _

from zope.app.apidoc.utilities import renderText, columnize
from zope.app.apidoc.codemodule.module import Module
from zope.app.apidoc.codemodule.class_ import Class
from zope.app.apidoc.codemodule.function import Function
from zope.app.apidoc.codemodule.text import TextFile
from zope.app.apidoc.codemodule.zcml import ZCMLFile


class ModuleDetails(object):
    """Represents the details of the module."""

    def getDoc(self):
        """Get the doc string of the module STX formatted."""
        text = self.context.getDocString()
        if text is None:
            return None
        lines = text.strip().split('\n')
        # Get rid of possible CVS id.
        lines = [line for line in lines if not line.startswith('$Id')]
        return renderText('\n'.join(lines), self.context.getPath())

    def getEntries(self, columns=True):
        """Return info objects for all modules and classes in this module."""
        entries = [{'name': name,
                    'url': zapi.absoluteURL(obj, self.request),
                    'ismodule': zapi.isinstance(obj, Module),
                    'isinterface': zapi.isinstance(
                         removeAllProxies(obj), InterfaceClass),
                    'isclass': zapi.isinstance(obj, Class),
                    'isfunction': zapi.isinstance(obj, Function),
                    'istextfile': zapi.isinstance(obj, TextFile),
                    'iszcmlfile': zapi.isinstance(obj, ZCMLFile)}
                   for name, obj in self.context.items()]
        entries.sort(lambda x, y: cmp(x['name'], y['name']))
        if columns:
            entries = columnize(entries)
        return entries

    def getBreadCrumbs(self):
        """Create breadcrumbs for the module path.

        We cannot reuse the the system's bread crumbs, since they go all the
        way up to the root, but we just want to go to the root module."""
        names = self.context.getPath().split('.') 
        crumbs = []
        module = self.context
        # I really need the class here, so remove the proxy.
        while removeSecurityProxy(module).__class__ is Module:
            crumbs.append(
                {'name': zapi.name(module),
                 'url': zapi.absoluteURL(module, self.request)}
                )
            module = zapi.getParent(module)

        crumbs.append(
            {'name': _('[top]'),
             'url': zapi.getMultiAdapter(
                      (module, self.request), name='absolute_url')()} )

        crumbs.reverse()
        return crumbs
