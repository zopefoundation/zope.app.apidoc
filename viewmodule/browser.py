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
"""Views/Presentation Module Views

$Id: browser.py,v 1.1 2004/02/19 20:46:43 philikon Exp $
"""
from types import ClassType

from zope.proxy import removeAllProxies
from zope.interface import Interface

from zope.app import zapi
from zope.app.pagetemplate.viewpagetemplatefile import ViewPageTemplateFile
from zope.app.publisher.browser.icon import IconViewFactory
from zope.app.apidoc.utilities import getPythonPath, getPermissionIds

__metaclass__ = type

class Menu:
    """Views module Menu"""

    def getPresentationTypes(self):
        """Get a list of presentation types."""
        return [{'name': path.split('.')[-1], 'path': path}
            for path in ['zope.publisher.interfaces.http.IHTTPRequest',
                         'zope.publisher.interfaces.browser.IBrowserRequest',
                         'zope.publisher.interfaces.xmlrpc.IXMLRPCRequest',
                         'zope.publisher.interfaces.ftp.IFTPRequest']
                ]

    def getInterfaceIds(self):
        """Get a list of the ids of all interfaces registered with the
        interface service."""
        service = zapi.getService(self, 'Interfaces')
        ids = service.searchInterfaceIds()
        ids.sort()
        return ids

class SkinLayerUsage:
    """View for skins, layers and usages."""

    def getSkins(self):
        return [{'name': skin, 'layers': layers}
                for skin, layers in self.context.getSkinLayerMapping().items()]


def _getFactoryData(factory):
    """Squeeze some useful information out of the view factory"""
    info = {'path': None, 'template': None, 'resource': None,
            'referencable': False}

    if hasattr(factory, '__name__') and \
       factory.__name__.startswith('SimpleViewClass'):
        info['path'] = factory.__module__ + '.SimpleViewClass'
        info['template'] = factory.index.filename 

    elif isinstance(factory, (str, unicode, float, int, list, tuple)):
        pass

    elif factory.__module__.startswith('zope.app.publisher.browser.viewmeta'):
        info['path'] = getPythonPath(factory.__bases__[0])
        info['referencable'] = True

    elif not hasattr(factory, '__name__'):
        info['path'] = getPythonPath(factory.__class__)
        info['referencable'] = True

    elif type(factory) in (type, ClassType):
        info['path'] = getPythonPath(factory)
        info['referencable'] = True

    else:
        info['path'] = getPythonPath(factory)
        info['referencable'] = True

    if isinstance(factory, IconViewFactory):
        info['resource'] = factory.rname

    return info
    

class ViewsDetails:
    """View for Views"""

    def __init__(self, context, request):
        self.context = context
        self.request = request

        service = zapi.getService(context, 'Interfaces')
        self.iface = service.getInterface(request['iface'])
        self.type = service.getInterface(request['type'])

        service = zapi.getService(context, 'Presentation')
        self.views = service.getRegisteredMatching(object=self.iface,
                                                   request=self.type)

        self.show_all = request.has_key('all')


    def getViewsByLayers(self):
        """Generate the data structure that is used to create the list of
        views."""
        result = []
        for layer, views in self.views.items():
            entries = []
            for required, provided, more_req, name, factories in views:
                if self.show_all or \
                       not (required is None or required is Interface):
                    entry = {'name' : name,
                             'required' : getPythonPath(required),
                             'type' : getPythonPath(more_req[0]),
                             'factory' : _getFactoryData(factories[-1])
                             }
                    # Educated choice of the attribute name
                    entry.update(getPermissionIds('publishTraverse',
                                                  klass=factories[-1]))
                    entries.append(entry)

            if entries:
                entries.sort(lambda x, y: cmp(x['name'], y['name']))
                result.append({'name': layer, 'views': entries})

        return result
