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
"""User Preferences Interfaces

$Id$
"""
__docformat__ = "reStructuredText"

import zope.interface
import zope.schema

from zope.app.container.interfaces import IReadContainer
from zope.app.location.interfaces import ILocation


class IPreferenceGroup(ILocation):
    """A group of preferences.

    This component represents a logical group of preferences. The preferences
    contained by this group is defined through the schema. The group has also
    a name by which it can be accessed.

    The fields specified in the schema *must* be available as attributes and
    items of the group instance. It is up to the implementation how this is
    realized, however, most often one will implement __setattr__ and
    __getattr__ as well as the common mapping API. 
    """

    id = zope.schema.TextLine(
        title=u"Id",
        description=u"The id of the group.",
        required=True)

    schema = zope.schema.InterfaceField(
        title=u"Schema",
        description=u"Schema describing the preferences of the group.",
        required=False)

    title = zope.schema.TextLine(
        title=u"Title",
        description=u"The title of the group used in the UI.",
        required=True)

    description = zope.schema.Text(
        title=u"Description",
        description=u"The description of the group used in the UI.",
        required=False)


class IPreferenceCategory(zope.interface.Interface):
    """A collection of preference groups.

    Objects providing this interface serve as groups of preference
    groups. This allows UIs to distinguish between high- and low-level
    prefernce groups.
    """


class IDefaultPreferenceProvider(zope.interface.Interface):
    """A root object providing default values for the entire preferences tree.

    Default preference providers are responsible for providing default values
    for all preferences. The way they get these values are up to the
    implementation.
    """

    preferences = zope.schema.Field(
        title = u"Default Preferences Root",
        description = u"Link to the default preferences")
