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
"""Class Module Views

$Id: browser.py,v 1.1 2004/02/19 20:46:40 philikon Exp $
"""
import os
import inspect

from zope.interface import implementedBy
from zope.configuration.config import ConfigurationContext
from zope.security.checker import getCheckerForInstancesOf
from zope.proxy import removeAllProxies

from zope.app import zapi
from zope.app.apidoc.utilities import \
     getPythonPath, stx2html, getPermissionIds, getFunctionSignature, \
     getPublicAttributes, getInterfaceForAttribute

def _getTypeLink(type):
    path = getPythonPath(type)
    if path.startswith('__builtin__'):
        return None
    return path
    
class ClassDetails(object):
    """Represents the details of the class"""

    def __init__(self, context, request):
        self.context = context
        self.request = request
        self.path = request['path']
        self.klass = ConfigurationContext().resolve(self.path)
        self.checker = getCheckerForInstancesOf(self.klass)
        self.interfaces = list(implementedBy(self.klass))
        all_ifaces = {}
        for iface in self.interfaces:
            all_ifaces[iface] = 1
            for base in iface.getBases():
                all_ifaces[base] = 1
        self._all_ifaces = all_ifaces.keys()

    def getBases(self):
        """Get all bases of this class"""
        return [getPythonPath(base) for base in self.klass.__bases__]

    def getInterfaces(self):
        """Get all interfaces of this class."""
        return [getPythonPath(iface) for iface in self.interfaces]

    def getAttributes(self):
        """Get all attributes of this class."""
        attrs = []
        for name in getPublicAttributes(self.klass):
            attr = getattr(self.klass, name)
            if not inspect.ismethod(attr):
                entry = {'name': name,
                         'value': attr.__repr__(),
                         'type': type(attr).__name__,
                         'type_link': _getTypeLink(type(attr)),
                         'interface': getInterfaceForAttribute(
                                         name, self._all_ifaces)}
                entry.update(getPermissionIds(name, self.checker))
                attrs.append(entry)
        return attrs

    def getMethods(self):
        """Get all methods of this class."""
        methods = []
        for name in getPublicAttributes(self.klass):
            attr = getattr(self.klass, name)
            if inspect.ismethod(attr):
                entry = {'name': name,
                         'signature': getFunctionSignature(attr),
                         'doc': stx2html(attr.__doc__ or ''),
                         'interface': getInterfaceForAttribute(
                                          name, self._all_ifaces)}
                entry.update(getPermissionIds(name, self.checker))
                methods.append(entry)
        return methods

    def getDoc(self):
        """Get the doc string of the class."""
        return stx2html(self.klass.__doc__ or '')


class ModuleDetails(object):
    """ """

    def __init__(self, context, request):
        self.context = context
        self.request = request
        self.module_name = request.get('module', '')
        if self.module_name:
            self.module = __import__(self.module_name, {}, {}, ('*',))

    def isRoot(self):
        return self.module_name == ''

    def getEntries(self):
        if self.isRoot():
            return [{'name': name, 'path': name, 'module': True}
                    for name in self.context.rootModules]
        entries = []
        # Detect packages
        if self.module.__file__.endswith('__init__.pyc'):
            dir = os.path.split(self.module.__file__)[0]
            for file in os.listdir(dir):
                path = os.path.join(dir, file)
                if os.path.isdir(path) and '__init__.py' in os.listdir(path):
                    entries.append(
                        {'name': file,
                         'path': self.module.__name__ + '.' + file,
                         'module': True})
                elif os.path.isfile(path) and file.endswith('.py') and \
                         not file.startswith('__init__'):
                    entries.append(
                        {'name': file[:-3],
                         'path': self.module.__name__ + '.' + file[:-3],
                         'module': True})

        for name in self.module.__dict__.keys():
            attr = getattr(self.module, name)
            if `attr`.startswith('<class'):
                entries.append(
                    {'name': name,
                     'path': attr.__module__ + '.' + attr.__name__,
                     'module': False})
                
        entries.sort(lambda x, y: cmp(x['name'], y['name']))
        return entries

    def getEntriesInColumns(self, columns=3):
        entries = self.getEntries()
        per_col = len(entries)/3 + 1
        columns = []
        col = []
        in_col = 0
        for entry in entries:
            if in_col < per_col:
                col.append(entry)
                in_col += 1
            else:
                columns.append(col)
                col = [entry]
                in_col = 1
        if col:
            columns.append(col)
        return columns
            
        
    def getBreadCrumbs(self):
        names = self.module_name.split('.') 
        mods = []
        for i in xrange(len(names)):
            mods.append(
                {'name': names[i],
                 'path': '.'.join(names[:i+1])}
                )
        return mods
