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
"""ZCML Element Views

"""
__docformat__ = "reStructuredText"

from zope.configuration.fields import GlobalInterface
from zope.configuration.fields import GlobalObject
from zope.configuration.fields import Tokens
from zope.interface.interfaces import IInterface
from zope.schema import getFieldNamesInOrder
from zope.security.proxy import isinstance
from zope.security.proxy import removeSecurityProxy
from zope.traversing.api import getParent
from zope.traversing.browser import absoluteURL

from zope.app.apidoc.browser.utilities import findAPIDocumentationRoot
from zope.app.apidoc.browser.utilities import findAPIDocumentationRootURL
from zope.app.apidoc.codemodule.interfaces import IRootDirective
from zope.app.apidoc.interfaces import IDocumentationModule
from zope.app.apidoc.utilities import getPythonPath
from zope.app.apidoc.utilities import isReferencable
from zope.app.apidoc.zcmlmodule import quoteNS


def findDocModule(obj):
    if IDocumentationModule.providedBy(obj):
        return obj
    return findDocModule(getParent(obj))


def _compareAttrs(x, nameOrder):
    if x['name'] in nameOrder:
        valueX = nameOrder.index(x['name'])
    else:
        valueX = 999999
    return valueX


class DirectiveDetails:
    """Details about ZCML directives."""

    context = None
    request = None

    def fullTagName(self):
        context = removeSecurityProxy(self.context)
        ns, name = context.name
        if context.prefixes.get(ns):
            return '{}:{}'.format(context.prefixes[ns], name)
        return name

    def line(self):
        return str(removeSecurityProxy(self.context).info.line)

    def highlight(self):
        if self.request.get('line') == self.line():
            return 'highlight'
        return ''

    def url(self):
        directive = removeSecurityProxy(self.context)
        subDirective = None
        # Sub-directives are not directly documented, so use parent
        parent = getParent(directive)
        if not (IRootDirective.providedBy(parent) or
                IRootDirective.providedBy(directive)):
            subDirective = directive
            directive = parent
        ns, name = directive.name
        # Sometimes ns is `None`, especially in the slug files, where no
        # namespaces are used.
        ns = quoteNS(ns or 'ALL')
        zcml = findAPIDocumentationRoot(self.context, self.request)['ZCML']
        if name not in zcml[ns]:
            ns = 'ALL'
        link = '{}/ZCML/{}/{}/index.html'.format(
            findAPIDocumentationRootURL(self.context, self.request), ns, name)
        if subDirective:
            link += '#' + subDirective.name[1]
        return link

    def objectURL(self, value, field, rootURL):
        naked = removeSecurityProxy(self.context)
        bound = field.bind(naked.context)
        obj = bound.fromUnicode(value)
        if obj is None:
            return
        try:
            isInterface = IInterface.providedBy(obj)
        except (AttributeError, TypeError):  # pragma: no cover
            # probably an object that does not like to play nice with the CA
            isInterface = False

        # The object might be an instance; in this case get a link to the class
        if not hasattr(obj, '__name__'):  # pragma: no cover
            obj = getattr(obj, '__class__')
        path = getPythonPath(obj)
        if isInterface:
            apidoc_url = findAPIDocumentationRootURL(
                self.context, self.request)
            return '{}/Interface/{}/index.html'.format(apidoc_url, path)
        if isReferencable(path):
            return rootURL + '/%s/index.html' % (path.replace('.', '/'))

    def attributes(self):
        context = removeSecurityProxy(self.context)
        attrs = [{'name': (ns and context.prefixes[ns] + ':' or '') + name,
                  'value': value, 'url': None, 'values': []}
                 for (ns, name), value in context.attrs.items()]

        names = context.schema.names(True)
        rootURL = absoluteURL(findDocModule(self), self.request)
        for attr in attrs:
            name = (
                attr['name'] if attr['name'] in names else attr['name'] + '_')
            field = context.schema.get(name)

            if isinstance(field, (GlobalObject, GlobalInterface)):
                attr['url'] = self.objectURL(attr['value'], field, rootURL)

            elif isinstance(field, Tokens):
                field = field.value_type
                values = attr['value'].strip().split()
                if len(values) == 1:
                    attr['value'] = values[0]
                    attr['url'] = self.objectURL(values[0], field, rootURL)
                else:
                    for value in values:
                        if isinstance(field,
                                      (GlobalObject, GlobalInterface)):
                            url = self.objectURL(value, field, rootURL)
                        else:  # pragma: no cover
                            break
                        attr['values'].append({'value': value, 'url': url})

        # Make sure that the attributes are in the same order they are defined
        # in the schema.
        fieldNames = getFieldNamesInOrder(context.schema)
        fieldNames = [name.endswith('_') and name[:-1] or name
                      for name in fieldNames]
        attrs.sort(key=lambda x: _compareAttrs(x, fieldNames))

        if not IRootDirective.providedBy(context):
            return attrs

        xmlns = []
        for uri, prefix in context.prefixes.items():
            name = ':' + prefix if prefix else ''
            xmlns.append({'name': 'xmlns' + name,
                          'value': uri,
                          'url': None,
                          'values': []})

        xmlns.sort(key=lambda x: x['name'])
        return xmlns + attrs

    def hasSubDirectives(self):
        return len(removeSecurityProxy(self.context).subs) != 0

    def getElements(self):
        context = removeSecurityProxy(self.context)
        return context.subs
