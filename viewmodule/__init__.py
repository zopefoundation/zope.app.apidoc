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
from zope.app import zapi
from zope.interface import implements, classImplements, Interface, Attribute
from zope.component.presentation import SkinRegistration
from zope.component.presentation import DefaultSkinRegistration
from zope.component.presentation import LayerRegistration
from zope.app.apidoc.interfaces import IDocumentationModule
from zope.app.apidoc.utilities import relativizePath
from zope.app.i18n import ZopeMessageIDFactory as _
from zope.app.location import locate

# TODO: Temporary hack, since registering an adapter for a particular class is
# broken.
class ISkinRegistration(Interface): pass
classImplements(SkinRegistration, ISkinRegistration)

class ILayerRegistration(Interface): pass
classImplements(LayerRegistration, ILayerRegistration)


class ISkinDocumentation(Interface):
    """Provides useful information of skins for documentation."""

    name = Attribute("""Name of the skin.""")

    layers = Attribute("A list of ILayerDocumentation objects that represent "
                       "the layers of this skin.")

    doc = Attribute("A string that describes the skin and/or its origin.")

    default = Attribute("Set to true, if the skin is the default skin.")


class ILayerDocumentation(Interface):
    """Provides useful information of layers for documentation."""

    name = Attribute("""Name of the layer.""")

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

        Examples::

          >>> module = ViewModule()
          >>> skins = [skin.name for skin in module.getSkins()]
          >>> skins.sort()
          >>> skins
          ['skinA', 'skinB', 'skinC']

          >>> pres = zapi.getGlobalService('Presentation')
          >>> pres.defineSkin('skinD', ['layer3'])
          >>> skins = [skin.name for skin in module.getSkins()]
          >>> skins.sort()
          >>> skins
          ['skinA', 'skinB', 'skinC', 'skinD']
        """ 
        # Only the global presentation service defines skins 
        service = zapi.getGlobalService('Presentation')
        skins = [ISkinDocumentation(reg)
                 for reg in service.registrations()
                 if isinstance(reg, SkinRegistration)]
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

      >>> pres = zapi.getGlobalService('Presentation')
      >>> reg = pres._registrations[('skin', 'skinA')]
      >>> doc = SkinDocumentation(reg)
      >>> doc.name
      'skinA'
      >>> doc.default
      True
      >>> pprint(doc.layers)
      [LayerDocumentation('default')]

      >>> reg = pres._registrations[('skin', 'skinC')]
      >>> doc = SkinDocumentation(reg)
      >>> doc.name
      'skinC'
      >>> doc.default
      False
      >>> pprint(doc.layers)
      [LayerDocumentation('layer4'),
       LayerDocumentation('layer2'),
       LayerDocumentation('layer1'),
       LayerDocumentation('default')]
    """
    implements(ISkinDocumentation)

    def __init__(self, context):
        self.__parent__ = context
        self.context = context

    # See ISkinDocumentation
    name = property(lambda self: self.context.skin)

    def isDefault(self):
        """Return whether this skin is the default skin."""
        service = zapi.getService('Presentation')
        for registration in service.registrations():
            if isinstance(registration, DefaultSkinRegistration) and \
                   registration.skin == self.context.skin:
                return True
        return False

    # See ISkinDocumentation
    default = property(isDefault)

    def getLayers(self):
        """Get a list of all layers in this skin.

        Each element of the list is a LayerDocumentation component.
        """
        service = zapi.getService('Presentation')
        layers = [ILayerDocumentation(reg)
                  for reg in service.registrations()
                  if (isinstance(reg, LayerRegistration) and
                      reg.layer in self.context.layers)]

        
        if 'default' in self.context.layers:
            default = LayerRegistration('default',
                                        'This is a predefined layer.')
            layers.append(ILayerDocumentation(default))

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
            self.name, self.context.layers)        


class LayerDocumentation(object):
    """Adapter for global layer registration objects.

    This is used as a wrapper to output end-user friendlier information. We
    also always want the documentation of a layer registration to be a string,
    which the `LayerRegistration.doc` attribute does not guarantee. 

    Examples::

      >>> from zope.app.apidoc.tests import pprint

      >>> LayerRegistration = type('LayerRegistration', (object,),
      ...                          {'layer': u'help', 'doc': u'documentation'})

      >>> ParserInfo = type('ParserInfo', (object,),
      ...                   {'file': u'Zope3/src/zope/app/configure.zcml',
      ...                    'line': 5})

      >>> reg = LayerRegistration()
      >>> layerdoc = LayerDocumentation(reg)
      >>> layerdoc.name
      u'help'
      >>> layerdoc.doc
      u'documentation'

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
    name = property(lambda self: self.context.layer)

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
