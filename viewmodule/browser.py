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

$Id: browser.py,v 1.7 2004/03/30 02:01:18 srichter Exp $
"""
from types import ClassType

from zope.interface import Interface

from zope.app import zapi
from zope.app.publisher.browser.icon import IconViewFactory
from zope.app.apidoc.utilities import getPythonPath, getPermissionIds
from zope.app.apidoc.utilities import columnize, relativizePath
from zope.app.component.interface import searchInterfaceIds
from zope.app.component.interface import getInterface


class Menu(object):
    """Views module Menu"""

    def getPresentationTypes(self):
        """Get a list of presentation types.

        Currently the presentation types are hard coded, which will change,
        once we define types for them.

        Example::

          >>> from zope.app.apidoc.tests import pprint
          >>> menu = Menu()
          >>> types = menu.getPresentationTypes()
          >>> pprint(types)
          [[('name', 'IHTTPRequest'),
            ('path', 'zope.publisher.interfaces.http.IHTTPRequest')],
           [('name', 'IBrowserRequest'),
            ('path', 'zope.publisher.interfaces.browser.IBrowserRequest')],
           [('name', 'IXMLRPCRequest'),
            ('path', 'zope.publisher.interfaces.xmlrpc.IXMLRPCRequest')],
           [('name', 'IFTPRequest'),
            ('path', 'zope.publisher.interfaces.ftp.IFTPRequest')]]
        """
        return [{'name': path.split('.')[-1], 'path': path}
            for path in ['zope.publisher.interfaces.http.IHTTPRequest',
                         'zope.publisher.interfaces.browser.IBrowserRequest',
                         'zope.publisher.interfaces.xmlrpc.IXMLRPCRequest',
                         'zope.publisher.interfaces.ftp.IFTPRequest']
                ]

    def getInterfaceIds(self):
        """Get a list of the ids of all interfaces registered with the
        interface service.

        Example::

          >>> menu = Menu()
          >>> menu.getInterfaceIds()
          ['IBrowserRequest', 'IFoo']
        """
        ids = searchInterfaceIds(self)
        ids.sort()
        return ids


class SkinLayer(object):
    """View for skins and layers."""

    def getSkins(self, columns=True):
        """Get all skins and their layers.

        Example::

          >>> from zope.app.apidoc.tests import pprint
          >>> from zope.app.apidoc.viewmodule import ViewModule
          >>> view = SkinLayer()
          >>> view.context = ViewModule()
          >>> skins = view.getSkins(False)
          >>> pprint(skins)
          [[('layers', ('default',)), ('name', 'default')],
           [('layers', ('default',)), ('name', 'skinA')],
           [('layers', ('layer5', 'layer4', 'default')), ('name', 'skinB')],
           [('layers', ('layer4', 'layer2', 'layer1', 'default')),
            ('name', 'skinC')]]
        """
        info = [{'name': skin, 'layers': layers}
                for skin, layers in self.context.getSkinLayerMapping().items()]
        if columns:
            info = columnize(info)
        return info


def _getFactoryData(factory):
    """Squeeze some useful information out of the view factory

    Examples::

      >>> from zope.app.apidoc.tests import pprint

      The factory is a SimpleViewClass for a Page Template:

      >>> from zope.app.pagetemplate.simpleviewclass import SimpleViewClass
      >>> view = SimpleViewClass('index.pt')
      >>> info = _getFactoryData(view)
      >>> pprint(info)
      [('path', 'zope.app.pagetemplate.simpleviewclass.simple'),
       ('referencable', True),
       ('resource', None),
       ('template', 'Zope3/src/zope/app/apidoc/viewmodule/index.pt'),
       ('url', 'zope/app/pagetemplate/simpleviewclass/simple')]
 
      The factory is a simple type:
      
      >>> info = _getFactoryData(3)
      >>> pprint(info)
      [('path', None),
       ('referencable', False),
       ('resource', None),
       ('template', None),
       ('url', None)]

      The factory is an instance:

      >>> class Factory(object):
      ...     pass

      >>> info = _getFactoryData(Factory())
      >>> pprint(info)
      [('path', 'zope.app.apidoc.viewmodule.browser.Factory'),
       ('referencable', True),
       ('resource', None),
       ('template', None),
       ('url', 'zope/app/apidoc/viewmodule/browser/Factory')]

      The factory is a class or type:

      >>> info = _getFactoryData(Factory)
      >>> pprint(info)
      [('path', 'zope.app.apidoc.viewmodule.browser.Factory'),
       ('referencable', True),
       ('resource', None),
       ('template', None),
       ('url', 'zope/app/apidoc/viewmodule/browser/Factory')]
      
    """
    info = {'path': None, 'url': None, 'template': None, 'resource': None,
            'referencable': True}

    if hasattr(factory, '__name__') and \
       factory.__name__.startswith('SimpleViewClass'):
        # In the case of a SimpleView, the base is really what we are
        # interested in. Usually the first listed class is the interesting one.
        base = factory.__bases__[0]
        info['path'] = base.__module__ + '.' + base.__name__
        info['template'] = relativizePath(factory.index.filename)

    elif isinstance(factory, (str, unicode, float, int, list, tuple)):
        info['referencable'] = False

    elif factory.__module__.startswith('zope.app.publisher.browser.viewmeta'):
        info['path'] = getPythonPath(factory.__bases__[0])

    elif hasattr(factory, '__name__') and factory.__name__ == 'proxyView':
        if hasattr(factory, 'factory'):
            factory = factory.factory
        info['path'] = factory.__module__ + '.' + factory.__name__

    elif not hasattr(factory, '__name__'):
        info['path'] = getPythonPath(factory.__class__)

    elif type(factory) in (type, ClassType):
        info['path'] = getPythonPath(factory)

    else:
        info['path'] = getPythonPath(factory)

    if info['referencable']:
        info['url'] = info['path'].replace('.', '/')

    if isinstance(factory, IconViewFactory):
        info['resource'] = factory.rname

    return info
    

class ViewsDetails(object):
    """View for Views"""

    def __init__(self, context, request):
        """Initialize the view."""
        self.context = context
        self.request = request

        self.iface = getInterface(self.context, request['iface'])
        self.type = getInterface(self.context, request['type'])

        # XXX: The local presentation service does not have a
        # getRegisteredMatching() method. Sigh. 
        service = zapi.getService(None, 'Presentation')
        self.views = service.getRegisteredMatching(object=self.iface,
                                                   request=self.type)

        self.show_all = request.has_key('all')


    def getViewsByLayers(self):
        """Generate the data structure that is used to create the list of
        views.

        Example::

          >>> from zope.app.apidoc.tests import pprint
          >>> from zope.publisher.browser import TestRequest
        
          >>> form ={'iface': 'IFoo',
          ...        'type': 'IBrowserRequest'}
          >>> view = ViewsDetails(None, TestRequest(form=form))
          >>> layer = view.getViewsByLayers()[0]
          >>> layer['name']
          'default'
          >>> view = layer['views'][0]
          >>> pprint(view)
          [('factory',
            [('path', 'zope.app.apidoc.viewmodule.tests.FooView'),
             ('referencable', True),
             ('resource', None),
             ('template', None),
             ('url', 'zope/app/apidoc/viewmodule/tests/FooView')]),
           ('name', u'index.html'),
           ('provided', 'zope.interface.Interface'),
           ('read_perm', None),
           ('required', 'zope.app.apidoc.viewmodule.tests.IFoo'),
           ('type', 'zope.publisher.interfaces.browser.IBrowserRequest'),
           ('write_perm', None)]
        """
        result = []
        for layer, views in self.views.items():
            entries = []
            for required, provided, more_req, name, factory in views:
                if self.show_all or \
                       not (required is None or required is Interface):
                    entry = {'name' : name or '<i>no name</i>',
                             'required' : getPythonPath(required),
                             'type' : getPythonPath(more_req[0]),
                             'factory' : _getFactoryData(factory),
                             'provided' : getPythonPath(provided)
                             }
                    # Educated choice of the attribute name
                    entry.update(getPermissionIds('publishTraverse',
                                                  klass=factory))
                    entries.append(entry)

            if entries:
                entries.sort(lambda x, y: cmp(x['name'], y['name']))
                result.append({'name': layer, 'views': entries})

        return result
