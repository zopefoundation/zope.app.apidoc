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
"""Interface Module Browser Menu (Tree)

A list of interfaces from the global site manager is pretty much unmanagable and
is very confusing. Therefore it is nice to split the path of the interface, so
that we get a deeper tree with nodes having shorter, manageable names.

$Id$
"""
__docformat__ = 'restructuredtext'
from zope.security.proxy import removeSecurityProxy

def getAllTextOfInterface(iface):
    """Get all searchable text from an interface

    Example:

    >>> import zope.interface
    >>> import zope.schema
    >>> class IFoo(zope.interface.Interface):
    ...     '''foo'''
    ...
    ...     def bar(self):
    ...         '''bar'''
    ...
    ...     blah = zope.interface.Attribute('blah', 'blah')
    ...
    ...     field = zope.schema.Field(
    ...         title = u'title', description = u'description')
    
    Now get the text. Note that there is no particular order during the text
    collection.
    
    >>> text = getAllTextOfInterface(IFoo)
    >>> u'foo' in text
    True
    >>> u'bar' in text
    True
    >>> u'blah' in text
    True
    >>> u'field' in text
    True
    >>> u'title' in text
    True
    >>> u'description' in text
    True
    """
    iface = removeSecurityProxy(iface)
    text = iface.__doc__ or ''
    for name in iface:
        attr = iface[name]
        text += attr.getName()
        text += attr.getDoc()
    return text


class Menu(object):
    """Menu for the Interface Documentation Module.

    The menu allows for looking for interfaces by full-text search or partial
    names. See `findInterfaces()` for the simple search implementation.
    """

    def findInterfaces(self):
        """Find the interface that match any text in the documentation strings
        or a partial path.

        Before we can test the method, let's create a Menu instance:

        >>> from zope.interface.interfaces import IElement, IAttribute

        >>> menu = Menu()
        >>> menu.context = {'IElement': IElement, 'IAttribute': IAttribute}
        >>> menu.request = {'name_only': 'on', 'search_str': ''}

        Now let's see how successful our searches are:

        >>> from zope.app.apidoc.tests import pprint
        >>> menu.request['search_str'] = 'Elem'
        >>> pprint(menu.findInterfaces())
        [[('name', 'IElement'), ('url', './IElement/apiindex.html')]]

        >>> menu.request['search_str'] = 'I'
        >>> pprint(menu.findInterfaces())
        [[('name', 'IAttribute'), ('url', './IAttribute/apiindex.html')],
         [('name', 'IElement'), ('url', './IElement/apiindex.html')]]

        Now using the full text search:

        >>> del menu.request['name_only']

        >>> menu.request['search_str'] = 'object'
        >>> pprint(menu.findInterfaces())
        [[('name', 'IAttribute'), ('url', './IAttribute/apiindex.html')],
         [('name', 'IElement'), ('url', './IElement/apiindex.html')]]

        >>> menu.request['search_str'] = 'Stores'
        >>> pprint(menu.findInterfaces())
        [[('name', 'IAttribute'), ('url', './IAttribute/apiindex.html')]]
        """
        name_only = ('name_only' in self.request) and True or False
        search_str = self.request.get('search_str', None)
        results = []
        
        if search_str is None:
            return results
        for name, iface in self.context.items():
            if (search_str in name or
                (not name_only and search_str in getAllTextOfInterface(iface))):
                results.append(
                    {'name': name,
                     'url': './%s/apiindex.html' %name
                     })
        results.sort(lambda x, y: cmp(x['name'], y['name']))
        return results
