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
"""Configuration File Representation

$Id$
"""
__docformat__ = "reStructuredText"

from persistent import Persistent
from xml.dom import minidom
from xml.parsers.expat import ExpatError

from zope.cachedescriptors.property import Lazy
from zope.configuration import xmlconfig
from zope.configuration.config import ConfigurationContext
from zope.configuration.zopeconfigure import IZopeConfigure
from zope.interface import implements
from zope.schema import getFields
from zope.schema.interfaces import IFromUnicode

import zope.app.appsetup.appsetup
from zope.app import zapi
from zope.app.location import locate
from zope.app.container.contained import Contained

from interfaces import IElement, IComment, IDirective, IConfiguration

context = None
def getContext():
    global context
    if context is None:
        context = xmlconfig.file(zope.app.appsetup.appsetup.getConfigSource(),
                                 execute=False)
    return context


class Element(Contained):
    """A wrapper for a Mini-DOM Element to provide a Python/Zope-native
    representation.
    """
    implements(IElement)
    
    def __init__(self, dom):
        """Initialize the Element object."""
        self.domElement = dom

    def _getSubElement(self, dom, index):
        """Helper method to create new element."""
        element = Element(dom)
        locate(element, self, unicode(index))
        return element

    def get(self, key, default=None):
        """See zope.app.container.interfaces.IReadContainer"""        
        try:
            return self[key]
        except KeyError:
            return default

    def keys(self):
        """See zope.app.container.interfaces.IReadContainer"""        
        dom = self.domElement
        return [unicode(index) for index in range(len(dom.childNodes))
                if dom.childNodes[index].nodeType != dom.TEXT_NODE]

    def values(self):
        """See zope.app.container.interfaces.IReadContainer"""        
        return [self[key] for key in self.keys()]

    def items(self):
        """See zope.app.container.interfaces.IReadContainer"""        
        return [(key, self[key]) for key in self.keys()]

    def __iter__(self):
        """See zope.app.container.interfaces.IReadContainer"""        
        return iter(self.keys())

    def __len__(self):
        """See zope.app.container.interfaces.IReadContainer"""        
        return len(self.keys())

    def __contains__(self, key):
        """See zope.app.container.interfaces.IReadContainer"""        
        try:
            index = int(key)
        except ValueError:
            raise KeyError, '%s cannot be converted to an index.' %key
        return index >= 0 and index < len(self.domElement.childNodes) and \
               self.domElement.childNodes[index] != self.domElement.TEXT_NODE

    def __getitem__(self, key):
        """See zope.app.container.interfaces.IReadContainer"""        
        try:
            index = int(key)
        except ValueError:
            raise KeyError, '%s cannot be converted to an index.' %key
        # Create the sub-element from the index and give it a location before
        # returning it.
        element = self._getSubElement(self.domElement.childNodes[index], index)
        locate(element, self, key)
        return element

    def getElementType(self):
        """See configeditor.interfaces.IElement"""
        return self.domElement.nodeType


class Comment(Element):
    """ """
    implements(IComment)

    def getValue(self):
        return self.domElement.nodeValue
    value = property(getValue)


class Directive(Element):
    """ """
    implements(IDirective)
    
    def __init__(self, dom, tagName=None, namespaceURI=None,
                 attributes=None, config=None):
        self.domElement = dom
        self.config = config
        # Delay lookup till later
        self.schema = None

    def _getSubElement(self, dom, index):
        """Helper method to create new element."""
        if dom.nodeType == dom.ELEMENT_NODE:
            element = Directive(dom, config=self.config)
            element.schema = self.config.getSchema(
                dom.namespaceURI, dom.localName, self.schema)
        elif dom.nodeType == dom.COMMENT_NODE:
            element = Comment(dom)
        else:
            element = Element(dom)
        locate(element, self, unicode(index))
        return element

    def getFullTagName(self):
        """See configeditor.interfaces.IDirective"""
        return self.domElement.tagName
        
    def getAttribute(self, name):
        """See configeditor.interfaces.IDirective"""
        if name not in self.schema  and name+'_' not in self.schema:
            raise AttributeError, "'%s' not in schema" %name
        return self.domElement.getAttribute(name)

    def getAttributeMap(self):
        """See configeditor.interfaces.IDirective"""
        return dict(self.domElement.attributes.items())
    
    def getAvailableSubdirectives(self):
        """ """
        registry = self.config._registry
        return [
            ((ns, name), schema) 
            for (ns, name), schema, usedIn, handler, info, parent in registry
            if parent and self.schema.isOrExtends(parent.schema)]
        

class Configuration(Directive):
    """Cofiguration Object"""
    implements(IConfiguration)

    def __init__(self, filename, package, parent=None, name=None):
        # Retrieve the directive registry
        self.filename = filename
        self.package = package
        self.__parent__ = parent
        self.__name__ = name
        self.config = self
        self.schema = None
                      

    def _registry(self):
        return getContext()._docRegistry
    _registry = property(_registry)
        
    def domElement(self):
        domElement = self.parse()
        self.schema = self.getSchema(domElement.namespaceURI,
                                     domElement.localName)
        return domElement
    domElement = Lazy(domElement)

    def parse(self):
        """See configeditor.interfaces.IConfiguration"""
        return minidom.parse(self.filename).getElementsByTagName('configure')[0]

    def getSchema(self, namespaceURI, tagName, parentSchema=None):
        """See configeditor.interfaces.IConfiguration"""
        if parentSchema is IZopeConfigure:
            parentSchema = None
        for (ns, name), schema, usedIn, handler, info, pDir in self._registry:
            if ((ns == namespaceURI or ns == '') and name == tagName and
                ((pDir is None and parentSchema is None) or
                 (pDir is not None and parentSchema is pDir.schema))):
                return schema
        return None

    def getNamespacePrefix(self, namespaceURI):
        """ """
        for name, value in self.getAttributeMap().items():
            if name.startswith('xmlns') and value == namespaceURI:
                if name == 'xmlns':
                    return ''
                else:
                    return name[6:]
        return None

    def getNamespaceURI(self, prefix):
        """ """
        for name, value in self.getAttributeMap().items():
            if name == 'xmlns' and prefix == '':
                return value
            if name.startswith('xmlns') and name.endswith(prefix):
                return value

        return None

    def getResolver(self):
        """ """
        if self.package is None:
            return None
        resolver = ConfigurationContext()
        resolver.package = self.package
        resolver.i18n_domain = self.domElement.getAttribute('i18n_domain')
        resolver.i18n_strings = {}
        resolver.actions = []
        from zope.configuration.xmlconfig import ParserInfo
        resolver.info = ParserInfo(self.filename, 0, 0)
        return resolver
