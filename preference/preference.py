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
"""User Preference System

$Id$
"""
__docformat__ = "reStructuredText"
from BTrees.OOBTree import OOBTree

import zope.interface
from zope.schema import getFields
from zope.security.checker import CheckerPublic, Checker, defineChecker
from zope.security.management import getInteraction

from zope.app import zapi
from zope.app.container.contained import Contained
from zope.app.location import LocationProxy, locate
from zope.app.principalannotation.interfaces import IPrincipalAnnotationUtility

from zope.app.apidoc.utilities import ReadContainerBase
from zope.app.apidoc.preference import interfaces

pref_key = 'zope.app.user.UserPreferences'

class PreferencesGroup(object):

    zope.interface.implements(interfaces.IPreferencesGroup)

    name = None
    schema = None
    title = None

    def __init__(self, name, schema, title=u''):
        self.name = name
        self.schema = schema
        self.title = title
        zope.interface.directlyProvides(self, self.schema)

    def __getattr__(self, key):
        if key in self.schema:
            marker = object()
            value = self.annotations.get(key, marker)
            if value is marker:
                return self.schema[key].default
            return value
        raise AttributeError, "'%s' is not a preference." %key

    def __setattr__(self, key, value):
        if self.schema and key in self.schema:
            # Validate the value
            bound = self.schema[key].bind(self)
            bound.validate(value)
            # Assign value
            self.annotations[key] = value
        else:
            self.__dict__[key] = value
            
    def annotations(self):
        utility = zapi.getUtility(IPrincipalAnnotationUtility)
        # TODO: what if we have multiple participations
        principal = getInteraction().participations[0].principal
        ann = utility.getAnnotations(principal)

        if  ann.get(pref_key) is None:
            ann[pref_key] = OOBTree()
        prefs = ann[pref_key]

        if self.name not in prefs.keys():
            prefs[self.name] = OOBTree()

        return prefs[self.name]
    annotations = property(annotations)


def PreferencesGroupChecker(instance):
    """A function that can be registered as a Checker in defineChecker()"""
    read_perm_dict = {'name': CheckerPublic, 'schema': CheckerPublic,
                      'title': CheckerPublic}
    write_perm_dict = {}

    for name in getFields(instance.schema):
        read_perm_dict[name] = CheckerPublic
        write_perm_dict[name] = CheckerPublic

    return Checker(read_perm_dict, write_perm_dict)

defineChecker(PreferencesGroup, PreferencesGroupChecker)


class UserPreferences(ReadContainerBase, Contained):

    zope.interface.implements(interfaces.IUserPreferences)

    def get(self, key, default=None):
        """See zope.app.container.interfaces.IReadContainer"""
        group = zapi.queryUtility(interfaces.IPreferencesGroup, key, default)
        if group == default:
            return default
        return LocationProxy(group, self, key)

    def items(self):
        """See zope.app.container.interfaces.IReadContainer"""
        items = list(zapi.getUtilitiesFor(interfaces.IPreferencesGroup))
        return [(key, LocationProxy(group, self, key))
                for key, group in items]


class preferencesNamespace(object):
    """Used to traverse to an User Preferences."""
    def __init__(self, ob, request=None):
        self.context = ob
        
    def traverse(self, name, ignore):
        prefs = UserPreferences()
        locate(prefs, self.context, '++preferences++')
        if not name:
            return prefs
        return prefs[name]
