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
"""Class Views

$Id: browser.py 29143 2005-02-14 22:43:16Z srichter $
"""
__docformat__ = 'restructuredtext'
import types
from zope.proxy import removeAllProxies
from zope.security.proxy import removeSecurityProxy

from zope.app import zapi
from zope.app.apidoc.interfaces import IDocumentationModule
from zope.app.apidoc.utilities import getPythonPath, getPermissionIds
from zope.app.apidoc.utilities import renderText, getFunctionSignature


def getTypeLink(type):
    if type is types.NoneType:
        return None
    path = getPythonPath(type)
    return path.replace('.', '/')

class ClassDetails(object):
    """Represents the details of the class."""

    def getBases(self):
        """Get all bases of this class.

        Example::

          The class we are using for this view is
          zope.app.apidoc.classmodule.ClassModule.

          >>> import pprint
          >>> from tests import getClassDetailsView
          >>> view = getClassDetailsView()

          >>> pprint.pprint(view.getBases())
          [{'path': 'zope.app.apidoc.classmodule.Module',
            'url': 'http://127.0.0.1/zope/app/apidoc/classmodule/Module'}]
        """
        return self._listClasses(self.context.getBases())


    def getKnownSubclasses(self):
        """Get all known subclasses of this class.

        Example::

          The class we are using for this view is
          zope.app.apidoc.classmodule.ClassModule.

          >>> import pprint
          >>> from tests import getClassDetailsView
          >>> view = getClassDetailsView()

          >>> pprint.pprint(view.getKnownSubclasses())
          []
        """
        entries = self._listClasses(self.context.getKnownSubclasses())
        entries.sort(lambda x, y: cmp(x['path'], y['path']))
        return entries

    def _listClasses(self, classes):
        """Prepare a list of classes for presentation.

        Example::

          >>> import pprint
          >>> from tests import getClassDetailsView
          >>> view = getClassDetailsView()
          >>> import zope.app.apidoc
          >>> import zope.app.apidoc.classmodule

          >>> pprint.pprint(view._listClasses([
          ...       zope.app.apidoc.APIDocumentation,
          ...       zope.app.apidoc.classmodule.Module]))
          [{'path': 'zope.app.apidoc.APIDocumentation',
            'url': 'http://127.0.0.1/zope/app/apidoc/APIDocumentation'},
           {'path': 'zope.app.apidoc.classmodule.Module',
            'url': 'http://127.0.0.1/zope/app/apidoc/classmodule/Module'}]
        """
        info = []
        codeModule = zapi.getUtility(IDocumentationModule, "Code")
        for cls in classes:
            # We need to removeAllProxies because the security checkers for
            # zope.app.container.contained.ContainedProxy and
            # zope.app.i18n.messagecatalog.MessageCatalog prevent us from
            # accessing __name__ and __module__.
            unwrapped_cls = removeAllProxies(cls)
            path = getPythonPath(unwrapped_cls)
            try:
                klass = zapi.traverse(codeModule, path.replace('.', '/'))
                url = zapi.absoluteURL(klass, self.request)
            except TraversalError:
                # If one of the classes is implemented in C, we will not
                # be able to find it.
                url = None
            info.append({'path': path, 'url': url})
        return info


    def getBaseURL(self):
        """Return the URL for the API Documentation Tool.

        Example::

          >>> from tests import getClassDetailsView
          >>> view = getClassDetailsView()

          Note that the following output is a bit different than usual, since
          we have not setup all path elements.

          >>> view.getBaseURL()
          'http://127.0.0.1'
        """
        m = zapi.getUtility(IDocumentationModule, "Code")
        return zapi.absoluteURL(zapi.getParent(m), self.request)


    def getInterfaces(self):
        """Get all implemented interfaces (as paths) of this class.

        Example::

          The class we are using for this view is
          zope.app.apidoc.classmodule.ClassModule.

          >>> from zope.app.apidoc.tests import pprint
          >>> from tests import getClassDetailsView
          >>> view = getClassDetailsView()

          >>> pprint(view.getInterfaces())
          ['zope.app.apidoc.interfaces.IDocumentationModule',
           'zope.app.location.interfaces.ILocation',
           'zope.app.apidoc.classmodule.IModuleDocumentation',
           'zope.app.container.interfaces.IReadContainer']
        """
        return map(getPythonPath, self.context.getInterfaces())


    def getAttributes(self):
        """Get all attributes of this class.

        Example::

          The class we are using for this view is
          zope.app.apidoc.classmodule.ClassModule.

          >>> from zope.app.apidoc.tests import pprint
          >>> from tests import getClassDetailsView
          >>> view = getClassDetailsView()

          >>> attr = view.getAttributes()[1]
          >>> pprint(attr)
          [('interface', 'zope.app.apidoc.interfaces.IDocumentationModule'),
           ('name', 'title'),
           ('read_perm', None),
           ('type', 'MessageID'),
           ('type_link', 'zope.i18nmessageid.messageid.MessageID'),
           ('value', "u'Classes'"),
           ('write_perm', None)]
        """
        attrs = []
        for name, attr, iface in self.context.getAttributes():
            entry = {'name': name,
                     'value': `attr`,
                     'type': type(attr).__name__,
                     'type_link': getTypeLink(type(attr)),
                     'interface': getPythonPath(iface)}
            # Since checkers do not have security declarations on their API,
            # we have to remove the security wrapper to get to the API calls. 
            checker = self.context.getSecurityChecker()
            entry.update(
                getPermissionIds(name, removeSecurityProxy(checker)))
            attrs.append(entry)
        return attrs


    def getMethods(self):
        """Get all methods of this class.

        Example::

          The class we are using for this view is
          zope.app.apidoc.classmodule.ClassModule.

          >>> from zope.app.apidoc.tests import pprint
          >>> from tests import getClassDetailsView
          >>> view = getClassDetailsView()

          >>> methods = view.getMethods()
          >>> pprint(methods[-2:])
          [[('doc', u''),
            ('interface',
             'zope.interface.common.mapping.IEnumerableMapping'),
            ('name', 'keys'),
            ('read_perm', None),
            ('signature', '()'),
            ('write_perm', None)],
           [('doc', u''),
            ('interface',
             'zope.interface.common.mapping.IEnumerableMapping'),
            ('name', 'values'),
            ('read_perm', None),
            ('signature', '()'),
            ('write_perm', None)]]
        """
        methods = []
        # remove the security proxy, so that `attr` is not proxied. We could
        # unproxy `attr` for each turn, but that would be less efficient.
        #
        # `getPermissionIds()` also expects the class's security checker not
        # to be proxied.
        klass = removeSecurityProxy(self.context)
        for name, attr, iface in klass.getMethods():
            entry = {'name': name,
                     'signature': getFunctionSignature(attr),
                     'doc': renderText(attr.__doc__ or '',
                                       zapi.getParent(self.context).getPath()),
                     'interface': getPythonPath(iface)}
            entry.update(getPermissionIds(name, klass.getSecurityChecker()))
            methods.append(entry)
        return methods


    def getDoc(self):
        """Get the doc string of the class STX formatted.

        Example::

          The class we are using for this view is
          zope.app.apidoc.classmodule.ClassModule.

          >>> from tests import getClassDetailsView
          >>> view = getClassDetailsView()

          >>> print view.getDoc()[23:80]
          <p>Represent the Documentation of any possible class.</p>
        """
        return renderText(self.context.getDocString() or '',
                          zapi.getParent(self.context).getPath())

