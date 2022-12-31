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
"""ZCML File Representation
"""
__docformat__ = "reStructuredText"
import copy
from xml.sax import make_parser
from xml.sax.handler import feature_namespaces
from xml.sax.xmlreader import InputSource

import zope.app.appsetup.appsetup
from zope.cachedescriptors.property import Lazy
from zope.configuration import config
from zope.configuration import xmlconfig
from zope.interface import directlyProvides
from zope.interface import implementer
from zope.location.interfaces import ILocation

from zope.app.apidoc.codemodule.interfaces import IDirective
from zope.app.apidoc.codemodule.interfaces import IRootDirective
from zope.app.apidoc.codemodule.interfaces import IZCMLFile


class MyConfigHandler(xmlconfig.ConfigurationHandler):
    """Special configuration handler to generate an XML tree."""

    def __init__(self, context):
        super().__init__(context)
        self.rootElement = self.currentElement = None
        self.prefixes = {}

    def startPrefixMapping(self, prefix, uri):
        self.prefixes[uri] = prefix

    def evaluateCondition(self, expression):
        # We always want to process/show all ZCML directives.
        # The exception needs to be `installed` that evaluates to False;
        # if we can't load the package, we can't process the file
        arguments = expression.split(None)
        verb = arguments.pop(0)
        if verb in ('installed', 'not-installed'):
            return super().evaluateCondition(expression)
        return True

    def startElementNS(self, name, qname, attrs):
        # The last stack item is parent of the stack item that we are about to
        # create
        stackitem = self.context.stack[-1]
        super().startElementNS(name, qname, attrs)

        # Get the parser info from the correct context
        info = self.context.stack[-1].context.info

        # complex stack items behave a bit different than the other ones, so
        # we need to handle it separately
        if isinstance(stackitem, config.ComplexStackItem):
            schema = stackitem.meta.get(name[1])[0]
        else:
            schema = stackitem.context.factory(stackitem.context, name).schema

        # Now we have all the necessary information to create the directive
        element = Directive(name, schema, attrs, stackitem.context, info,
                            self.prefixes)
        # Now we place the directive into the XML directive tree.
        if self.rootElement is None:
            self.rootElement = element
        else:
            self.currentElement.subs.append(element)

        element.__parent__ = self.currentElement
        self.currentElement = element

    def endElementNS(self, name, qname):
        super().endElementNS(name, qname)
        self.currentElement = self.currentElement.__parent__


@implementer(IDirective)
class Directive:
    """Representation of a ZCML directive."""

    def __init__(self, name, schema, attrs, context, info, prefixes):
        self.name = name
        self.schema = schema
        self.attrs = attrs
        self.context = context
        self.info = info
        self.__parent__ = None
        self.subs = []
        self.prefixes = prefixes

    def __repr__(self):
        return '<Directive %s>' % str(self.name)


@implementer(ILocation, IZCMLFile)
class ZCMLFile:
    """Representation of an entire ZCML file."""

    def __init__(self, filename, package, parent, name):
        # Retrieve the directive registry
        self.filename = filename
        self.package = package
        self.__parent__ = parent
        self.__name__ = name

    def withParentAndName(self, parent, name):
        located = type(self)(self.filename, self.package, parent, name)
        # We don't copy the root element; let it parse again if needed, instead
        # of trying to recurse through all the children and copy them.
        return located

    @Lazy
    def rootElement(self):
        # Get the context that was originally generated during startup and
        # create a new context using its registrations
        real_context = zope.app.appsetup.appsetup.getConfigContext()
        context = config.ConfigurationMachine()
        context._registry = copy.copy(real_context._registry)
        context._features = copy.copy(real_context._features)
        context.package = self.package

        # Shut up i18n domain complaints
        context.i18n_domain = 'zope'

        # Since we want to use a custom configuration handler, we need to
        # instantiate the parser object ourselves
        parser = make_parser()
        handler = MyConfigHandler(context)
        parser.setContentHandler(handler)
        parser.setFeature(feature_namespaces, True)

        # Now open the file
        file = open(self.filename)
        src = InputSource(getattr(file, 'name', '<string>'))
        src.setByteStream(file)

        # and parse it
        parser.parse(src)

        # Finally we retrieve the root element, have it provide a special root
        # directive interface and give it a location, so that we can do local
        # lookups.
        root = handler.rootElement
        directlyProvides(root, IRootDirective)
        root.__parent__ = self
        return root
