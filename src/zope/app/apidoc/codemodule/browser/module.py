##############################################################################
#
# Copyright (c) 2004 Zope Foundation and Contributors.
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
"""Module Views

$Id$
"""
__docformat__ = 'restructuredtext'
from zope.component import getMultiAdapter
from zope.i18nmessageid import ZopeMessageFactory as _
from zope.interface.interfaces import IInterface
from zope.proxy import removeAllProxies
from zope.publisher.browser import BrowserView
from zope.security.proxy import isinstance
from zope.traversing.api import getParent
from zope.traversing.browser import absoluteURL

from zope.app.apidoc.apidoc import APIDocumentation
from zope.app.apidoc.utilities import getPythonPath, renderText
from zope.app.apidoc.codemodule.interfaces import IModuleDocumentation
from zope.app.apidoc.codemodule.interfaces import IClassDocumentation
from zope.app.apidoc.codemodule.interfaces import IFunctionDocumentation
from zope.app.apidoc.codemodule.interfaces import IZCMLFile
from zope.app.apidoc.codemodule.interfaces import ITextFile
from zope.app.apidoc.browser.utilities import findAPIDocumentationRootURL


def formatDocString(text, module=None, summary=False):
    """Format a doc string for display.

    module is either a Python module (from sys.modules) or the dotted name
    of a module.

    If summary is true, the result is plain text and includes only
    the summary part of the doc string.
    If summary is false, the result is HTML and includes the whole doc string.
    """
    if text is None:
        return None
    lines = text.strip().split('\n')
    # Get rid of possible CVS id.
    lines = [line for line in lines if not line.startswith('$Id')]
    if summary:
        for i in range(len(lines)):
            if not lines[i].strip():
                del lines[i:]
                break
        return '\n'.join(lines)
    return renderText('\n'.join(lines), module)


class ModuleDetails(BrowserView):
    """Represents the details of a module or package."""

    def __init__(self, context, request):
        super(ModuleDetails, self).__init__(context, request)
        items = list(self.context.items())
        items.sort()
        self.text_files = []
        self.zcml_files = []
        self.modules = []
        self.interfaces = []
        self.classes = []
        self.functions = []
        for name, obj in items:
            entry = {'name': name, 'url': absoluteURL(obj, self.request)}
            if IFunctionDocumentation.providedBy(obj):
                entry['doc'] = formatDocString(
                    obj.getDocString(), self.context.getPath())
                entry['signature'] = obj.getSignature()
                self.functions.append(entry)
            elif IModuleDocumentation.providedBy(obj):
                entry['doc'] = formatDocString(
                    obj.getDocString(), obj.getPath(), True)
                self.modules.append(entry)
            elif IInterface.providedBy(obj):
                entry['path'] = getPythonPath(removeAllProxies(obj))
                entry['doc'] = formatDocString(
                    obj.__doc__, obj.__module__, True)
                self.interfaces.append(entry)
            elif IClassDocumentation.providedBy(obj):
                entry['doc'] = formatDocString(
                    obj.getDocString(), self.context.getPath(), True)
                self.classes.append(entry)
            elif IZCMLFile.providedBy(obj):
                self.zcml_files.append(entry)
            elif ITextFile.providedBy(obj):
                self.text_files.append(entry)

    def getAPIDocRootURL(self):
        return findAPIDocumentationRootURL(self.context, self.request)

    def getDoc(self):
        """Get the doc string of the module, formatted as HTML."""
        return formatDocString(
            self.context.getDocString(), self.context.getPath())

    def getPath(self):
        """Return the path to the module"""
        return self.context.getPath()

    def isPackage(self):
        """Return true if this module is a package"""
        return self.context.isPackage()

    def getModuleInterfaces(self):
        """Return entries about interfaces the module provides"""
        entries = []
        for iface in self.context.getDeclaration():
            entries.append({
                'name': iface.__name__,
                'path': getPythonPath(removeAllProxies(iface))
            })
        return entries

    def getModules(self):
        """Return entries about contained modules and subpackages"""
        return self.modules

    def getInterfaces(self):
        """Return entries about interfaces declared by the module"""
        return self.interfaces

    def getClasses(self):
        """Return entries about classes declared by the module"""
        return self.classes

    def getTextFiles(self):
        """Return entries about text files contained in the package"""
        return self.text_files

    def getZCMLFiles(self):
        """Return entries about ZCML files contained in the package"""
        return self.zcml_files

    def getFunctions(self):
        """Return entries about functions declared by the package"""
        return self.functions
