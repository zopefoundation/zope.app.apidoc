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
"""User Preferences API

$Id$
"""
__docformat__ = "reStructuredText"

import zope.interface
import zope.schema

from zope.app.container.interfaces import IReadContainer

class IPreferencesGroup(zope.interface.Interface):
    """A group of preferences.

    This component represents a logical group of preferences. The preferences
    contained by this group is defined through the schema. The group has also
    a name by which it can be accessed.
    """

    name = zope.schema.TextLine(
        title=u"Name",
        description=u"The name of the group.",
        required=True)

    schema = zope.schema.InterfaceField(
        title=u"Schema",
        description=u"Schema describing the preferences of the group.",
        required=True)

    title = zope.schema.TextLine(
        title=u"Title",
        description=u"The title of the group used in the UI.",
        required=True)


class IUserPreferences(IReadContainer):
    """Component that manages all preference groups."""

    
