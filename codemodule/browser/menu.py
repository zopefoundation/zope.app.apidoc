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
"""Code Module Menu

$Id: browser.py 29143 2005-02-14 22:43:16Z srichter $
"""
__docformat__ = 'restructuredtext'
from zope.app import zapi
from zope.app.apidoc.interfaces import IDocumentationModule
from zope.app.apidoc.classregistry import classRegistry

class Menu(object):
    """Menu for the Class Documentation Module.

    The menu allows for looking for classes by partial names. See
    `findClasses()` for the simple search implementation.
    """

    def findClasses(self):
        """Find the classes that match a partial path.

        Examples::

          >>> from zope.app.apidoc.tests import pprint
          >>> from zope.app.apidoc.classmodule import Class
          >>> cm = zapi.getUtility(IDocumentationModule, 'Class')
          >>> mod = cm['zope']['app']['apidoc']['classmodule']['browser']

          Setup a couple of classes and register them.

          >>> class Foo(object):
          ...     pass
          >>> mod._Module__children['Foo'] = Class(mod, 'Foo', Foo)
          >>> class Foo2(object):
          ...     pass
          >>> mod._Module__children['Foo2'] = Class(mod, 'Foo2', Foo2)
          >>> class Blah(object):
          ...     pass
          >>> mod._Module__children['Blah'] = Class(mod, 'Blah', Blah)

          Setup the view.

          >>> from zope.publisher.browser import TestRequest
          >>> menu = Menu()
          >>> menu.context = None

          Testing the method with various inputs.
          
          >>> menu.request = TestRequest(form={'path': 'Foo'})
          >>> info = menu.findClasses()

          >>> pprint(info)
          [[('path', 'zope.app.apidoc.classmodule.browser.Foo'),
            ('url',
             'http://127.0.0.1/zope/app/apidoc/classmodule/browser/Foo')],
           [('path', 'zope.app.apidoc.classmodule.browser.Foo2'),
            ('url',
             'http://127.0.0.1/zope/app/apidoc/classmodule/browser/Foo2')]]
          
          >>> menu.request = TestRequest(form={'path': 'o2'})
          >>> info = menu.findClasses()
          >>> pprint(info)
          [[('path', 'zope.app.apidoc.classmodule.browser.Foo2'),
            ('url',
             'http://127.0.0.1/zope/app/apidoc/classmodule/browser/Foo2')]]
          
          >>> menu.request = TestRequest(form={'path': 'Blah'})
          >>> info = menu.findClasses()
          >>> pprint(info)
          [[('path', 'zope.app.apidoc.classmodule.browser.Blah'),
            ('url',
             'http://127.0.0.1/zope/app/apidoc/classmodule/browser/Blah')]]
        """
        path = self.request.get('path', None)
        if path is None:
            return []
        classModule = zapi.getUtility(IDocumentationModule, "Code")
        results = []
        for p in classRegistry.keys():
            if p.find(path) >= 0:
                klass = zapi.traverse(classModule, p.replace('.', '/'))
                results.append(
                    {'path': p,
                     'url': zapi.absoluteURL(klass, self.request)
                     })
        results.sort(lambda x, y: cmp(x['path'], y['path']))
        return results
