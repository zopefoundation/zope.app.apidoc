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
"""Views/Presentation Module Views

$Id$
"""
from types import ClassType, FunctionType

from zope.interface import Interface
from zope.component.adapter import AdapterRegistration
from zope.publisher.interfaces.browser import ILayer

from zope.publisher.interfaces.browser import IBrowserRequest
from zope.publisher.interfaces.xmlrpc import IXMLRPCRequest
from zope.publisher.interfaces.http import IHTTPRequest
from zope.publisher.interfaces.ftp import IFTPRequest

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
        site manager.

        Example::

          >>> menu = Menu()
          >>> u'IFoo' in menu.getInterfaceIds()
          True
          >>> u'IBrowserRequest' in menu.getInterfaceIds()
          True
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
         [SkinDocumentation(u'skinA', []),
          SkinDocumentation(u'skinB', [u'layer1', u'layer2']),
          SkinDocumentation(u'skinC', [u'layer3', u'layer2'])]
        """
        skins = self.context.getSkins()
        if columns:
            skins = columnize(skins, 2)
        return skins


def _getFactoryData(factory):
    """Squeeze some useful information out of the view factory

    Examples::

      >>> from zope.app.apidoc.tests import pprint

      The factory is a SimpleViewClass for a Page Template:

      >>> from zope.app.pagetemplate.simpleviewclass import SimpleViewClass
      >>> view = SimpleViewClass('index.pt')
      >>> info = _getFactoryData(view)

      Normalize pathname separators.
      >>> info['template'] = info['template'].replace('\\\\', '/')[-35:]
      >>> pprint(info)
      [('path', 'zope.app.pagetemplate.simpleviewclass.simple'),
       ('referencable', True),
       ('resource', None),
       ('template', 'zope/app/apidoc/viewmodule/index.pt'),
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

    elif hasattr(factory, '__class__') and \
             factory.__class__.__name__ == 'ProxyView':
        factory = factory.factory
        info['path'] = factory.__module__ + '.' + factory.__name__

    elif not hasattr(factory, '__name__'):
        info['path'] = getPythonPath(factory.__class__)

    elif type(factory) in (type, ClassType):
        info['path'] = getPythonPath(factory)

    elif isinstance(factory, FunctionType):
        info['path'] = getPythonPath(factory.factory)
    else:
        info['path'] = getPythonPath(factory)

    if info['referencable']:
        info['url'] = info['path'].replace('.', '/')

    if isinstance(factory, IconViewFactory):
        info['resource'] = factory.rname

    return info


def _getPresentationType(iface):
    """Get the presentation type from a layer interface.

    Examples::

      >>> class ILayer1(IBrowserRequest): pass
      >>> _getPresentationType(ILayer1)
      <InterfaceClass zope.publisher.interfaces.browser.IBrowserRequest>

      >>> class ILayer2(IHTTPRequest): pass
      >>> _getPresentationType(ILayer2)
      <InterfaceClass zope.publisher.interfaces.http.IHTTPRequest>

      >>> class ILayer3(Interface): pass
      >>> _getPresentationType(ILayer3)
      <InterfaceClass zope.app.apidoc.viewmodule.browser.ILayer3>
    """
    # Note that the order of the requests matters here, since we want to
    # inspect the most specific one first. For example, IBrowserRequest is also
    # an IHTTPRequest. 
    for type in [IBrowserRequest, IXMLRPCRequest, IHTTPRequest, IFTPRequest]:
        if iface.isOrExtends(type):
            return type
    return iface
    

class ViewsDetails(object):
    """View for Views"""

    def __init__(self, context, request):
        """Initialize the view."""
        self.context = context
        self.request = request

        self.iface = getInterface(self.context, request['iface'])
        self.type = getInterface(self.context, request['type'])

        self.show_all = request.has_key('all')

        sm = zapi.getSiteManager()
        # This is okay here, since we only read from the site manager. Once
        # registration objects have sensible security declarations, we can
        # remove that call. 
        from zope.proxy import removeAllProxies
        sm = removeAllProxies(sm)
        self.regs = [reg
                     for reg in sm.registrations()
                     if (isinstance(reg, AdapterRegistration) and
                         reg.required[-1] is not None and
                         # TODO: Handle multiple required ifaces at some point.
                         self.iface.isOrExtends(reg.required[0]
                                                or Interface) and
                         reg.required[-1].isOrExtends(self.type))]


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
          u'layer1'
          >>> view = layer['views'][0]
          >>> pprint(view)
          [('factory',
            [('path', 'zope.app.apidoc.viewmodule.tests.FooView'),
             ('referencable', True),
             ('resource', None),
             ('template', None),
             ('url', 'zope/app/apidoc/viewmodule/tests/FooView')]),
           ('info', ''),
           ('name', 'index.html'),
           ('provided', 'zope.interface.Interface'),
           ('read_perm', None),
           ('required', 'zope.app.apidoc.viewmodule.tests.IFoo'),
           ('type', 'zope.publisher.interfaces.browser.IBrowserRequest'),
           ('write_perm', None)]
        """
        entries = {}
        for reg in self.regs:
            if self.show_all or \
                   not (None in reg.required or Interface in reg.required):
                entry = {'name' : reg.name or '<i>no name</i>',
                         # TODO: Deal with tuple
                         'required' : getPythonPath(reg.required[0]),
                         'type' : getPythonPath(
                                      _getPresentationType(reg.required[-1])),
                         'factory' : _getFactoryData(reg.value),
                         'provided' : getPythonPath(reg.provided)
                         }

                if isinstance(reg.doc, (unicode, str)):
                    entry['info'] = reg.doc
                else:
                    # We can safely assume that we deal with a ParserInfo
                    # object here.
                    entry['info'] = '%s (line %s)' %(
                        relativizePath(reg.doc.file), reg.doc.line)

                # Educated choice of the attribute name
                entry.update(getPermissionIds('publishTraverse',
                                              klass=reg.value))

                # Determine the layer
                layer = reg.required[-1]
                name = [name for name, util in zapi.getUtilitiesFor(ILayer)
                        if util is layer]
                if name:
                    name = name[0]
                else:
                    name = '<no layer>'
                    
                layer = entries.setdefault(name, [])
                layer.append(entry)

        for entry in entries.values():
            entry.sort(lambda x, y: cmp(x['name'], y['name']))

        return [{'name': layer, 'views': views}
                for layer, views in entries.items()]
