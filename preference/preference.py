##############################################################################
#
# Copyright (c) 2005 Zope Corporation and Contributors.
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
"""User Preferences System

$Id$
"""
__docformat__ = "reStructuredText"
from BTrees.OOBTree import OOBTree

import zope.interface
from zope.schema import getFields
from zope.security.checker import CheckerPublic, Checker, defineChecker
from zope.security.management import getInteraction

from zope.app.container.interfaces import IReadContainer
from zope.app import zapi
from zope.app.container.contained import Contained
from zope.app.location import LocationProxy, locate, Location
from zope.app.principalannotation.interfaces import IPrincipalAnnotationUtility
from zope.app.traversing.interfaces import IContainmentRoot

from zope.app.apidoc.preference.interfaces import IPreferenceGroup 
from zope.app.apidoc.preference.interfaces import IPreferenceCategory 
from zope.app.apidoc.preference.interfaces import IDefaultPreferenceProvider 

pref_key = 'zope.app.user.UserPreferences'


class PreferenceGroup(Location):
    """A feature-rich ``IPreferenceGroup`` implementation.

    This class implements the 
    """
    zope.interface.implements(IPreferenceGroup, IReadContainer)

    # Declare attributes here, so that they are always available.
    id = None
    schema = None
    title = None
    description = None

    def __init__(self, id, schema=None, title=u'', description=u'',
                 isCategory=False):
        self.id = id
        self.schema = schema
        self.title = title
        self.description = description

        # The last part of the id is the name.
        self.__name__ = id.split('.')[-1]

        # Make sure this group provides all important interfaces.
        directlyProvided = ()
        if isCategory:
            directlyProvided += (IPreferenceCategory,)
        if schema:
            directlyProvided += (schema,)
        zope.interface.directlyProvides(self, directlyProvided)


    def __bind__(self, parent):
        clone = self.__class__.__new__(self.__class__)
        clone.__dict__.update(self.__dict__)
        clone.__parent__ = parent
        return clone


    def get(self, key, default=None):
        id = self.id and self.id + '.' + key or key
        group = zapi.queryUtility(IPreferenceGroup, id, default)
        if group is default:
            return default
        return group.__bind__(self)
    

    def items(self):
        cutoff = self.id and len(self.id)+1 or 0
        return [(id[cutoff:], group.__bind__(self))
                for id, group in zapi.getUtilitiesFor(IPreferenceGroup)
                if id != self.id and \
                   id.startswith(self.id) and \
                   id[cutoff:].find('.') == -1]


    def __getitem__(self, key):
        """See zope.app.container.interfaces.IReadContainer"""
        default = object()
        obj = self.get(key, default)
        if obj is default:
            raise KeyError, key
        return obj

    def __contains__(self, key):
        """See zope.app.container.interfaces.IReadContainer"""
        return self.get(key) is not None

    def keys(self):
        """See zope.app.container.interfaces.IReadContainer"""
        return [id for id, group in self.items()]

    def __iter__(self):
        """See zope.app.container.interfaces.IReadContainer"""
        return self.values().__iter__()
        
    def values(self):
        """See zope.app.container.interfaces.IReadContainer"""
        return [group for id, group in self.items()]

    def __len__(self):
        """See zope.app.container.interfaces.IReadContainer"""
        return len(self.items())    

    def __getattr__(self, key):
        # Try to find a sub-group of the given id
        group = self.get(key)
        if group is not None:
            return group

        # Try to find a preference of the given name
        if self.schema and key in self.schema:
            marker = object()
            value = self.data.get(key, marker)
            if value is marker:
                # Try to find a default preference provider
                provider = zapi.queryUtility(IDefaultPreferenceProvider)
                if provider is None:
                    return self.schema[key].default
                defaultGroup = provider.getDefaultPreferenceGroup(self.id)
                return getattr(defaultGroup, key)
            return value

        # Nothing found, raise an attribute error
        raise AttributeError, "'%s' is not a preference or sub-group." %key

    def __setattr__(self, key, value):
        if self.schema and key in self.schema:
            # Validate the value
            bound = self.schema[key].bind(self)
            bound.validate(value)
            # Assign value
            self.data[key] = value
        else:
            self.__dict__[key] = value

    def __delattr__(self, key):
        if self.schema and key in self.schema:
            del self.data[key]
        else:
            del self.__dict__[key]

    def data(self):
        utility = zapi.getUtility(IPrincipalAnnotationUtility)
        # TODO: what if we have multiple participations?
        principal = getInteraction().participations[0].principal
        ann = utility.getAnnotations(principal)

        # If no preferences exist, create the root preferences object.
        if  ann.get(pref_key) is None:
            ann[pref_key] = OOBTree()
        prefs = ann[pref_key]

        # If no entry for the group exists, create a new entry.
        if self.id not in prefs.keys():
            prefs[self.id] = OOBTree()

        return prefs[self.id]
    data = property(data)



def PreferenceGroupChecker(instance):
    """A function that can be registered as a Checker in defineChecker()

    The attributes available in a preference group are dynamically generated
    based on the group schema and the available sub-groups. Thus, the
    permission dictionaries have to be generated at runtime and are unique for
    each preference group instance.
    """
    read_perm_dict = {}
    write_perm_dict = {}

    # Make sure that the attributes from IPreferenceGroup and IReadContainer
    # are public.
    for attrName in ('id', 'schema', 'title', 'description',
                     'get', 'items', 'keys', 'values',
                     '__getitem__', '__contains__', '__iter__', '__len__'):
        read_perm_dict[attrName] = CheckerPublic

    # Make the attributes generated from the schema available as well.
    if instance.schema is not None:
        for name in getFields(instance.schema):
            read_perm_dict[name] = CheckerPublic
            write_perm_dict[name] = CheckerPublic

    # Make all sub-groups available as well.
    for name in instance.keys():
        read_perm_dict[name] = CheckerPublic
        write_perm_dict[name] = CheckerPublic

    return Checker(read_perm_dict, write_perm_dict)

defineChecker(PreferenceGroup, PreferenceGroupChecker)



class preferencesNamespace(object):
    """Used to traverse to the root preferences group."""

    def __init__(self, ob, request=None):
        self.context = ob
        
    def traverse(self, name, ignore):
        rootGroup = zapi.getUtility(IPreferenceGroup)
        rootGroup = rootGroup.__bind__(self.context)
        rootGroup.__name__ = '++preferences++'
        zope.interface.alsoProvides(rootGroup, IContainmentRoot)
        return name and rootGroup[name] or rootGroup
