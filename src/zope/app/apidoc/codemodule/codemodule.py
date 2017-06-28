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
"""Code Documentation Module

This module is able to take a dotted name of any class and display
documentation for it.

"""
__docformat__ = 'restructuredtext'

import zope.component
from zope.i18nmessageid import ZopeMessageFactory as _
from zope.interface import implementer

from zope.app.apidoc.interfaces import IDocumentationModule
from zope.app.apidoc.classregistry import safe_import
from zope.app.apidoc.codemodule.interfaces import IAPIDocRootModule
from zope.app.apidoc.codemodule.module import Module


@implementer(IDocumentationModule)
class CodeModule(Module):
    """Represent the code browser documentation root"""

    #: The title.
    title = _('Code Browser')

    #: The description.
    description = _("""
    This module allows you to get an overview of the modules and classes
    defined in the Zope 3 framework and its supporting packages. There are
    two methods to navigate through the modules to find the classes you are
    interested in.

    The first method is to type in some part of the Python path of the class
    and the module will look in the class registry for matches. The menu will
    then return with a list of these matches.

    The second method is to click on the "Browse Zope Source" link. In the
    main window, you will see a directory listing with the root Zope 3
    modules. You can click on the module names to discover their content. If a
    class is found, it is represented as a bold entry in the list.

    The documentation contents of a class provides you with an incredible
    amount of information. Not only does it tell you about its base classes,
    implemented interfaces, attributes and methods, but it also lists the
    interface that requires a method or attribute to be implemented and the
    permissions required to access it.
    """)

    def __init__(self):
        "Initialize object."
        super(CodeModule, self).__init__(None, '', None, False)
        self.__isSetup = False

    def setup(self):
        """Setup module and class tree."""
        if self.__isSetup:
            return
        self.__isSetup = True
        self._children = {}
        for name, mod in zope.component.getUtilitiesFor(IAPIDocRootModule):
            module = safe_import(mod)
            if module is not None:
                self._children[name] = Module(self, name, module)

    def withParentAndName(self, parent, name):
        located = type(self)()
        located.__parent__ = parent
        located.__name__ = name
        self.setup()
        located._children = {name: module.withParentAndName(located, name)
                             for name, module in self._children.items()}
        located.__isSetup = True
        return located

    def getDocString(self):
        return _('Zope 3 root.')

    def getFileName(self):
        return ''

    def getPath(self):
        return ''

    def isPackage(self):
        return True

    def get(self, key, default=None):
        self.setup()
        # TODO: Do we really like that this allows importing things from
        # outside our defined namespace? This can lead to a static
        # export with unreachable objects (not in the menu)
        return super(CodeModule, self).get(key, default)

    def items(self):
        self.setup()
        return super(CodeModule, self).items()

def _cleanUp():
    from zope.component import getGlobalSiteManager
    code = getGlobalSiteManager().queryUtility(IDocumentationModule, name='Code')
    if code is not None:
        code.__init__()

from zope.testing.cleanup import addCleanUp
addCleanUp(_cleanUp)
