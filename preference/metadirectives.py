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
"""``apidoc:preferencesgroup`` ZCML directive interface

$Id: metadirectives.py 26613 2004-07-18 21:50:40Z srichter $
"""
__docformat__ = 'restructuredtext'
from zope.interface import Interface
from zope.configuration import fields

class IPreferencesGroupDirective(Interface):
    """Register a preference group."""

    name = fields.PythonIdentifier(
        title=u"Name",
        description=u"Name of the preference group used to access the group.",
        required=True
        )

    schema = fields.GlobalInterface(
        title=u"Schema",
        description=u"Schema of the preference group used defining the "
                    u"preferences of the group.",
        required=True        
        )

    title = fields.MessageID(
        title=u"Title",
        description=u"Title of the preference group used in UIs.",
        required=True
        )
