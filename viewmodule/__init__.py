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
"""View Documentation Module

$Id$
"""
__docformat__ = 'restructuredtext'
from zope.interface import Interface, Attribute
from zope.interface import implements, classImplements, providedBy
from zope.publisher.interfaces.browser import ISkin, ILayer, IDefaultSkin

from zope.app import zapi
from zope.app.apidoc.interfaces import IDocumentationModule
from zope.app.apidoc.utilities import relativizePath, getPythonPath
from zope.app.i18n import ZopeMessageIDFactory as _
from zope.app.location import locate


class ISkinDocumentation(Interface):
    """Provides useful information of skins for documentation."""

    name = Attribute("""Name of the skin.""")

    interface = Attribute("""The interface that represents the skin.""")

    layers = Attribute("A list of ILayerDocumentation objects that represent "
                       "the layers of this skin.")

    doc = Attribute("A string that describes the skin and/or its origin.")

    default = Attribute("Set to true, if the skin is the default skin.")


class ILayerDocumentation(Interface):
    """Provides useful information of layers for documentation."""

    name = Attribute("""Name of the layer.""")

    interface = Attribute("""The interface that represents the layer.""")

    doc = Attribute("A string that describes the skin and/or its origin.")


class ViewModule(object):
    """Represent the Documentation of all Views."""

    implements(IDocumentationModule)

    # See zope.app.apidoc.interfaces.IDocumentationModule
    title = _('Presentations')

    # See zope.app.apidoc.interfaces.IDocumentationModule
    description = _("""
    The Presentations (or Views) module is somewhat crazy, since a view or
    resource cannot be identified by a single interface or name, but of four
    to five pieces of information. Conclusively, the menu lets you select an
    interface and a presentation type for which views should be found.

    By default, the resulting views exclude views that have no required
    interface (``None``) or are registered to require
    ``zope.interface.Interface``. To see these additional views, click on
    "Show all views".

    Once you click on "Show" you will be presented with a list of all
    applicable views. The views are sorted by layer. The views are mainly
    identified by name, since this is what you use in a URL for
    example. Information provided for each view include the required
    interface, the presentation type and the permission. If possible, the
    system also tries to extract some information from the factory, like the
    view class, the template or resource.

    Completely independent of all this, there is a link "Show Skins, Layers
    and Usages" that brings you to a simple screen that shows the mapping of
    the layers to skins and provides a list of available usages.
    """)

    def getSkins(self):
        """Get the names of all available skins.

        Example::

          >>> module = ViewModule()
          >>> skins = [skin.name for skin in module.getSkins()]
          >>> skins.sort()
          >>> skins
          [u'skinA', u'skinB', u'skinC']
        """ 
        # Only the global site manager defines skins
        sm = zapi.getGlobalSiteManager()
        skins = [SkinDocumentation(reg)
                 for reg in sm.registrations()
                 if reg.provided is ISkin and reg.name != '']
        skins.sort(lambda x, y: cmp(x.name, y.name))
        # Make sure skins have a location
        [locate(skin, self, skin.name) for skin in skins]
        return skins


class SkinDocumentation(object):
    """Adapter for global skin registration objects.

    This is used as a wrapper to output end-user friendlier information. We
    also always want the documentation of a layer registration to be a string,
    which the `LayerRegistration.doc` attribute does not guarantee. 

    Examples::

      >>> from zope.app.apidoc.tests import pprint

      >>> sm = zapi.getGlobalSiteManager()
      >>> reg = sm._registrations[(ISkin, 'skinA')]
      >>> doc = SkinDocumentation(reg)
      >>> doc.name
      u'skinA'
      >>> doc.default
      True
      >>> pprint(doc.layers)
      []
      >>> doc.interface
      'zope.app.apidoc.viewmodule.tests.SkinA'

      >>> reg = sm._registrations[(ISkin, 'skinC')]
      >>> doc = SkinDocumentation(reg)
      >>> doc.name
      u'skinC'
      >>> doc.default
      False
      >>> pprint(doc.layers)
      [LayerDocumentation(u'layer3'), LayerDocumentation(u'layer2')]
      >>> doc.interface
      'zope.app.apidoc.viewmodule.tests.SkinC'
    """
    implements(ISkinDocumentation)

    def __init__(self, context):
        self.__parent__ = context
        self.context = context

    # See ISkinDocumentation
    name = property(lambda self: self.context.name)

    # See ISkinDocumentation
    interface = property(lambda self: getPythonPath(self.context.component))

    def isDefault(self):
        """Return whether this skin is the default skin."""
        sm = zapi.getSiteManager()
        skin = sm.adapters.lookup((self.context.component,), IDefaultSkin, '')
        if skin is self.context.component:
            return True
        return False

    # See ISkinDocumentation
    default = property(isDefault)

    def getLayers(self):
        """Get a list of all layers in this skin.

        Each element of the list is a LayerDocumentation component.
        """
        sm = zapi.getSiteManager()
        layers = [LayerDocumentation(reg)
                  for reg in sm.registrations()
                  if reg.provided is ILayer and reg.name != '' and \
                     self.context.component.isOrExtends(reg.component)]
        
        # Make sure skins have a location
        [locate(layer, self, layer.name) for layer in layers]
        return layers
        
    # See ISkinDocumentation
    layers = property(getLayers)

    def getDoc(self):
        """Generate documentation."""
        if isinstance(self.context.doc, (str, unicode)):
            return self.context.doc

        # We can safely assume that for global skin registrations we have an
        # configuration info object.
        info = self.context.doc
        doc = _('$file (line $line)')
        doc.mapping = {'file': relativizePath(info.file),
                       'line': info.line}
        return doc

    # See ISkinDocumentation
    doc = property(getDoc)

    def __repr__(self):
        """Representation of the object in a doctest-friendly format."""
        return '%s(%r, %r)' % (
            self.__class__.__name__,
            self.name, [l.name for l in self.getLayers()])


class LayerDocumentation(object):
    """Adapter for global layer registration objects.

    This is used as a wrapper to output end-user friendlier information. We
    also always want the documentation of a layer registration to be a string,
    which the `LayerRegistration.doc` attribute does not guarantee. 

    Examples::

      >>> from zope.app.apidoc.tests import pprint

      >>> ParserInfo = type('ParserInfo', (object,),
      ...                   {'file': u'Zope3/src/zope/app/configure.zcml',
      ...                    'line': 5})

      >>> sm = zapi.getGlobalSiteManager()
      >>> reg = sm._registrations[(ILayer, 'layer1')]

      >>> layerdoc = LayerDocumentation(reg)
      >>> layerdoc.name
      u'layer1'
      >>> layerdoc.doc
      u'layer 1 doc'

      >>> reg.doc = ParserInfo()
      >>> layerdoc.doc
      u'$file (line $line)'
      >>> pprint(layerdoc.doc.mapping)
      [('file', u'Zope3/src/zope/app/configure.zcml'), ('line', 5)]
    """
    implements(ILayerDocumentation)

    def __init__(self, context):
        self.context = context

    # See ILayerDocumentation
    name = property(lambda self: self.context.name)

    # See ILayerDocumentation
    interface = property(lambda self: getPythonPath(self.context.component))

    def getDoc(self):
        """Generate documentation."""
        if isinstance(self.context.doc, (str, unicode)):
            return self.context.doc

        # We can safely assume that for global layer registrations we have an
        # configuration info object.
        info = self.context.doc
        doc = _('$file (line $line)')
        doc.mapping = {'file': relativizePath(info.file),
                       'line': info.line}
        return doc

    # See ILayerDocumentation
    doc = property(getDoc)

    def __repr__(self):
        """Representation of the object in a doctest-friendly format."""
        return '%s(%r)' % (self.__class__.__name__, self.name)        
