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
from zope.configuration.fields import GlobalObject, GlobalInterface
from zope.interface import implements
from zope.schema import getFieldNamesInOrder, getFieldsInOrder
from zope.schema.interfaces import IFromUnicode
from zope.security.proxy import removeSecurityProxy

from zope.app import zapi
from zope.app.tree.interfaces import IUniqueId
from zope.app.apidoc.interfaces import IDocumentationModule
from zope.app.apidoc.utilities import getPythonPath

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
        

class DisplayComment(object):

    value = property(lambda self: self.context.value)

    id = property(lambda self: IUniqueId(self.context).getId())


class DisplayDirective(object):

    id = property(lambda self: IUniqueId(self.context).getId())

    fullTagName = property(lambda self: self.context.getFullTagName())

    def url(self):
        # XXX: Determine URLs of directives that are in all namespaces
        context = removeSecurityProxy(self.context)
        ns = context.domElement.namespaceURI
        ns = ns.replace(':', '_co_')
        ns = ns.replace('/', '_sl_')
        zcml = zapi.getUtility(IDocumentationModule, 'ZCML')
        return '%s/../ZCML/%s/%s/index.html' %(
            zapi.absoluteURL(findDocModule(self), self.request), ns,
            context.domElement.localName)
        

    def attributes(self):
        schema = removeSecurityProxy(self.context.schema)
        resolver = self.context.config.getResolver()
        attrs = [{'name': name, 'value': value, 'url': None}
                 for name, value in self.context.getAttributeMap().items()]

        for attr in attrs:
            if name in schema:
                field = schema[name]
            elif name+'_' in schema:
                field = schema[name+'_']
            else:
                continue

            # XXX: This is extremly brittle!!!
            # Handle tokens; handle instances
            if isinstance(field, GlobalInterface):
                bound = field.bind(resolver)
                converter = IFromUnicode(bound)
                try:
                    value = converter.fromUnicode(attr['value'])
                except: continue
                attr['url'] = '%s/../Interface/%s/apiindex.html' %(
                    zapi.absoluteURL(findDocModule(self), self.request),
                    getPythonPath(value))

            elif isinstance(field, GlobalObject):
                bound = field.bind(resolver)
                converter = IFromUnicode(bound)
                # XXX: Fix later
                try:
                    value = converter.fromUnicode(attr['value'])
                except:
                    pass
                try:
                    attr['url'] = getPythonPath(value)                
                except AttributeError: continue

        # Make sure that the attributes are in the same order they are defined
        # in the schema.
        fieldNames = getFieldNamesInOrder(schema)
        fieldNames = [name.endswith('_') and name[:-1] or name
                      for name in fieldNames]
        attrs.sort(lambda x, y: _compareAttrs(x, y, fieldNames))

        return attrs

    def hasSubDirectives(self):
        return len(self.context) != 0

    def getElements(self):
        context = removeSecurityProxy(self.context)
        return context.values()
