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
"""Class Documentation Module

This module is able to take a dotted name of any class and display
documentation for it. 

$Id: __init__.py,v 1.1 2004/02/19 20:46:40 philikon Exp $
"""
from zope.app import zapi
from zope.interface import implements
from zope.app.apidoc.interfaces import IDocumentationModule


class ClassModule(object):
    """Represent the Documentation of any possible class."""

    implements(IDocumentationModule)

    # See zope.app.apidoc.interfaces.IDocumentationModule
    title = 'Classes'

    # See zope.app.apidoc.interfaces.IDocumentationModule
    description = """
    Since there is no registry for implemented classes for Zope 3, the user
    experience of this module is somewhat different than the others. Two
    alternative navigation means are provided. In the menu of the module you
    will see an input field in which you can type the dotted name of the
    desired class; for example 'zope.app.location.LocationProxy'. Once you
    press enter or click on "Show" you can see the documentation for the
    class.

    The second method is to click on the "Browse Zope Source" link. In the
    main window, you will see a directory listing with the root Zope 3
    modules. You can click on the module names to discover their content. If a
    class is found, it is represented as a bold entry in the list.

    The documentation contents of a class provides you with an incredible
    amount of information. Not only does it tell you about its base classes,
    implemented interfaces, attributes and methods, but it also lists the
    interface that requires a method or attribute to be implemented and the
    permissions required to access it. 
    """

    rootModules = ['ZConfig', 'persistence', 'transaction', 'zdaemon',
                   'zodb', 'zope']
