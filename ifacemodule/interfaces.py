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
"""Interface Documentation Module Interfaces

$Id$
"""
__docformat__ = "reStructuredText"
import zope.interface
import zope.schema

class IInterfaceDetailsPreferences(zope.interface.Interface):
    """
    Preferences for API Docs' Interface Details Screen

    It is possible to hide and show various sections of the interface details'
    screen. The following preferences allow you to choose the sections to be
    shown by default.
    """

    showSpecificRequiredAdapters = zope.schema.Bool(
        title=u"Specific Required Interface Adapters",
        description=u"Show specific required interface adapters",
        required=False,
        default=True)

    showExtendedRequiredAdapters = zope.schema.Bool(
        title=u"Extended Required Interface Adapters",
        description=u"Show extended required interface adapters",
        required=False,
        default=True)

    showGenericRequiredAdapters = zope.schema.Bool(
        title=u"Generic Required Interface Adapters",
        description=u"Show generic required interface adapters",
        required=False,
        default=False)

    showBrowserViews = zope.schema.Bool(
        title=u"Browser Views",
        description=u"Show browser views",
        required=False,
        default=True)

    showSpecificBrowserViews = zope.schema.Bool(
        title=u"Specific Browser Views",
        description=u"Show specific browser views",
        required=False,
        default=True)

    showExtendedBrowserViews = zope.schema.Bool(
        title=u"Extended Browser Views",
        description=u"Show extended browser views",
        required=False,
        default=False)

    showGenericBrowserViews = zope.schema.Bool(
        title=u"Generic Browser Views",
        description=u"Show generic browser views",
        required=False,
        default=False)

    showXMLRPCViews = zope.schema.Bool(
        title=u"XML-RPC Views",
        description=u"Show XML-RPC views",
        required=False,
        default=False)

    showSpecificXMLRPCViews = zope.schema.Bool(
        title=u"Specific XML-RPC Views",
        description=u"Show specific XML-RPC views",
        required=False,
        default=True)

    showExtendedXMLRPCViews = zope.schema.Bool(
        title=u"Extended XML-RPC Views",
        description=u"Show extended XML-RPC views",
        required=False,
        default=False)

    showGenericXMLRPCViews = zope.schema.Bool(
        title=u"Generic XML-RPC Views",
        description=u"Show generic XML-RPC views",
        required=False,
        default=False)

    showHTTPViews = zope.schema.Bool(
        title=u"Generic HTTP Views",
        description=u"Show generic HTTP views",
        required=False,
        default=False)

    showSpecificHTTPViews = zope.schema.Bool(
        title=u"Specific HTTP Views",
        description=u"Show specific HTTP views",
        required=False,
        default=True)

    showExtendedHTTPViews = zope.schema.Bool(
        title=u"Extended HTTP Views",
        description=u"Show extended HTTP views",
        required=False,
        default=False)

    showGenericHTTPViews = zope.schema.Bool(
        title=u"Generic HTTP Views",
        description=u"Show generic HTTP views",
        required=False,
        default=False)

    showFTPViews = zope.schema.Bool(
        title=u"FTP Views",
        description=u"Show FTP views",
        required=False,
        default=False)

    showSpecificFTPViews = zope.schema.Bool(
        title=u"Specific FTP Views",
        description=u"Show specific FTP views",
        required=False,
        default=True)

    showExtendedFTPViews = zope.schema.Bool(
        title=u"Extended FTP Views",
        description=u"Show extended FTP views",
        required=False,
        default=False)

    showGenericFTPViews = zope.schema.Bool(
        title=u"Generic FTP Views",
        description=u"Show generic FTP views",
        required=False,
        default=False)

    showOtherViews = zope.schema.Bool(
        title=u"Other Views",
        description=u"Show other (unidentified) views",
        required=False,
        default=False)

    showSpecificOtherViews = zope.schema.Bool(
        title=u"Specific Other Views",
        description=u"Show specific other views",
        required=False,
        default=True)

    showExtendedOtherViews = zope.schema.Bool(
        title=u"Extended Other Views",
        description=u"Show extended other views",
        required=False,
        default=False)

    showGenericOtherViews = zope.schema.Bool(
        title=u"Generic Other Views",
        description=u"Show generic other views",
        required=False,
        default=False)
    
