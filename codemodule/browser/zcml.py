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
"""ZCML Element Views

$Id$
"""
__docformat__ = "reStructuredText"
from zope.configuration.fields import GlobalObject, GlobalInterface, Tokens
from zope.interface import implements
from zope.interface.interfaces import IInterface
from zope.schema import getFieldNamesInOrder, getFieldsInOrder
from zope.schema.interfaces import IFromUnicode
from zope.security.proxy import removeSecurityProxy

from zope.app import zapi
from zope.app.tree.interfaces import IUniqueId
from zope.app.apidoc.interfaces import IDocumentationModule
from zope.app.apidoc.utilities import getPythonPath

from zope.app.apidoc.codemodule.interfaces import IRootDirective

def findDocModule(obj):
    if IDocumentationModule.providedBy(obj):
        return obj
    return findDocModule(zapi.getParent(obj))

def _compareAttrs(x, y, nameOrder):
    if x['name'] in nameOrder:
        valueX = nameOrder.index(x['name'])
    else:
        valueX = 999999

    if y['name'] in nameOrder:
        valueY = nameOrder.index(y['name'])
    else:
        valueY = 999999

    return cmp(valueX, valueY)


class DirectiveDetails(object):

    def fullTagName(self):
        context = removeSecurityProxy(self.context)
        ns, name = context.name
        if context.prefixes[ns]:
            return '%s:%s' %(context.prefixes[ns], name)
        else:
            return name

    def line(self):
        return str(removeSecurityProxy(self.context).info.line)

    def highlight(self):
        if self.request.get('line') == self.line():
            return 'highlight'
        return ''

    def url(self):
        context = removeSecurityProxy(self.context)
        ns, name = context.name
        ns = ns.replace(':', '_co_')
        ns = ns.replace('/', '_sl_')
        zcml = zapi.getUtility(IDocumentationModule, 'ZCML')
        if name not in zcml[ns]:
            ns = 'ALL'
        return '%s/../ZCML/%s/%s/index.html' %(
            zapi.absoluteURL(findDocModule(self), self.request), ns, name)
        
    def ifaceURL(self, value, field, rootURL):
        bound = field.bind(self.context.context)
        iface = bound.fromUnicode(value)
        return rootURL+'/../Interface/%s/apiindex.html' %(getPythonPath(iface))
  
    def objectURL(self, value, field, rootURL):
        bound = field.bind(self.context.context)
        obj = bound.fromUnicode(value)
        if IInterface.providedBy(obj):
            return rootURL+'/../Interface/%s/apiindex.html' %(
                getPythonPath(obj))
        try:
            return rootURL + '/%s/index.html' %(
                getPythonPath(obj).replace('.', '/'))
        except AttributeError:
            # probably an instance
            pass

    def attributes(self):
        context = removeSecurityProxy(self.context)
        attrs = [{'name': (ns and context.prefixes[ns]+':' or '') + name,
                  'value': value, 'url': None, 'values': []}
                 for (ns, name), value in context.attrs.items()]

        names = context.schema.names(True)
        rootURL = zapi.absoluteURL(findDocModule(self), self.request)
        for attr in attrs:
            name = (attr['name'] in names) and attr['name'] or attr['name']+'_'
            field = context.schema.get(name)
            if zapi.isinstance(field, GlobalInterface):
                attr['url'] = self.ifaceURL(attr['value'], field, rootURL)
                
            elif zapi.isinstance(field, GlobalObject):
                attr['url'] = self.objectURL(attr['value'], field, rootURL)

            elif zapi.isinstance(field, Tokens):
                field = field.value_type
                values = attr['value'].strip().split()
                if len(values) == 1:
                    attr['value'] = values[0]
                    if zapi.isinstance(field, GlobalInterface):
                        attr['url'] = self.ifaceURL(values[0], field, rootURL)
                    elif zapi.isinstance(field, GlobalObject):
                        attr['url'] = self.objectURL(values[0], field, rootURL)
                    break
                    
                for value in values: 
                    if zapi.isinstance(field, GlobalInterface):
                        url = self.ifaceURL(value, field, rootURL)
                    elif zapi.isinstance(field, GlobalObject):
                        url = self.objectURL(value, field, rootURL)
                    else:
                        break
                    attr['values'].append({'value': value, 'url': url})
                    

        # Make sure that the attributes are in the same order they are defined
        # in the schema.
        fieldNames = getFieldNamesInOrder(context.schema)
        fieldNames = [name.endswith('_') and name[:-1] or name
                      for name in fieldNames]
        attrs.sort(lambda x, y: _compareAttrs(x, y, fieldNames))

        if not IRootDirective.providedBy(context):
            return attrs

        xmlns = []
        for uri, prefix in context.prefixes.items():
            name = prefix and ':'+prefix or ''
            xmlns.append({'name': 'xmlns'+name,
                          'value': uri,
                          'url': None,
                          'values': []})

        xmlns.sort(lambda x, y: cmp(x['name'], y['name']))
        return xmlns + attrs

    def hasSubDirectives(self):
        return len(removeSecurityProxy(self.context).subs) != 0

    def getElements(self):
        context = removeSecurityProxy(self.context)
        return context.subs
