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
"""Code Module Menu

"""
__docformat__ = 'restructuredtext'
import operator

from zope.traversing.api import traverse
from zope.traversing.browser import absoluteURL

from zope.app.apidoc.classregistry import classRegistry

_pathgetter = operator.itemgetter("path")

class Menu(object):
    """Menu for the Class Documentation Module.

    The menu allows for looking for classes by partial names. See
    `findClasses()` for the simple search implementation.
    """

    context = None
    request = None

    def findClasses(self):
        """Find the classes that match a partial path.

        Examples::
          >>> from zope.app.apidoc.codemodule.class_ import Class

          Setup the view.

          >>> from zope.app.apidoc.codemodule.browser.menu import Menu
          >>> from zope.publisher.browser import TestRequest
          >>> menu = Menu()
          >>> menu.context = apidoc['Code']

          Testing the method with various inputs.

          >>> menu.request = TestRequest(form={'path': 'menu'})
          >>> info = menu.findClasses()

          >>> from pprint import pprint
          >>> pprint(info)
          [{'path': 'zope.app.apidoc.codemodule.browser.menu.Men',
            'url': 'http://127.0.0.1/++apidoc++/Code/zope/app/apidoc/codemodule/browser/menu/Menu/'},
           {'path': 'zope.app.apidoc.ifacemodule.menu.Men',
            'url': 'http://127.0.0.1/++apidoc++/Code/zope/app/apidoc/ifacemodule/menu/Menu/'}]

          >>> menu.request = TestRequest(form={'path': 'illegal name'})
          >>> info = menu.findClasses()
          >>> pprint(info)
          []

        """
        path = self.request.get('path', None)
        if path is None:
            return []
        classModule = traverse(self.context, '/++apidoc++')['Code']
        classModule.setup()
        found = [p for p in classRegistry if path in p]
        results = []
        for p in found:
            klass = traverse(classModule, p.replace('.', '/'))
            results.append({
                'path': p,
                'url': absoluteURL(klass, self.request) + '/'
            })
        results.sort(key=_pathgetter)
        return results

    def findAllClasses(self):

        """Find all classes

        Examples::

          Setup the view.

          >>> from zope.app.apidoc.codemodule.browser.menu import Menu
          >>> from zope.publisher.browser import TestRequest
          >>> menu = Menu()
          >>> menu.context = apidoc['Code']

          Make sure we're registered.

          >>> traverse(menu.context, 'zope/app/apidoc/codemodule/browser/menu')
          <zope.app.apidoc.codemodule.module.Module 'menu' at ...>

          Testing the method with various inputs.

          >>> menu.request = TestRequest(form={'path': 'Foo'})
          >>> info = menu.findAllClasses()

          >>> info = [x for x in info if x['path'] == 'zope.app.apidoc.codemodule.browser.menu.Menu']
          >>> len(info)
          1
        """
        classModule = traverse(self.context, '/++apidoc++')['Code']
        classModule.setup() # run setup if not yet done
        results = []
        counter = 0

        for p in list(classRegistry): # Traversing can potentially change the registry
            klass = traverse(classModule, p.replace('.', '/'))
            results.append({
                'path': p,
                'url': absoluteURL(klass, self.request),
                'counter': counter
            })
            counter += 1

        results.sort(key=_pathgetter)
        return results
