##############################################################################
#
# Copyright (c) 2004 Zope Corporation and Contributors.
# All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.0 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
##############################################################################
"""View Documentation Module

$Id: __init__.py,v 1.1 2004/02/19 20:46:43 philikon Exp $
"""
from zope.app import zapi
from zope.interface import implements
from zope.app.apidoc.interfaces import IDocumentationModule

__metaclass__ = type

class ViewModule:
    """Represent the Documentation of all Views."""

    implements(IDocumentationModule)

    # See zope.app.apidoc.interfaces.IDocumentationModule
    title = 'Presentations'

    # See zope.app.apidoc.interfaces.IDocumentationModule
    description = """
    The Presentations (or Views) module is somewhat crazy, since a view or
    resource cannot be identified by a single interface or name, but of four
    to five pieces of information. Conclusively, the menu let's you select an
    interface and a presentation type for which views should be found.

    By default, the resulting views exclude views that have no required
    interface ('None') or are registered to require
    'zope.interface.Interface'. To see these additional views, click on
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
    """
    
    def getSkins(self):
        """Get the names of all available skins.""" 
        service = zapi.getService(self, 'Presentation')
        return service.skins.keys()

    def getLayersForSkin(self, skin):
        """Get the names of all available layers of a particular skin.

        Returns a 'KeyError', if the skin does not exist.
        """ 
        service = zapi.getService(self, 'Presentation')
        return service.skins[skin]
        
    def getSkinLayerMapping(self):
        """Return a dictionary with keys being skin names and the value are
        tuples of layer names.""" 
        service = zapi.getService(self, 'Presentation')
        return service.skins

    def getUsages(self):
        """Return a list of all available usages."""
        service = zapi.getService(self, 'Presentation')
        return service._usages.keys()
        
