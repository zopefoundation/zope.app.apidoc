========================================
 Module Menu and ZCML Directive Details
========================================

.. currentmodule:: zope.app.apidoc.zcmlmodule.browser

:class:`Menu`
=============

Let's start out by creating a menu. First we instantiate the class:

  >>> from zope.app.apidoc.zcmlmodule.browser import Menu
  >>> menu = Menu()

then we create a ZCML module instance:

  >>> from zope.publisher.browser import TestRequest
  >>> module = apidoc.get('ZCML')
  >>> menu.context = module
  >>> menu.request = TestRequest()

Now we create a namespace representing directives available in all namespaces

  >>> from zope.app.apidoc.zcmlmodule import Namespace
  >>> ns = Namespace(module, 'ALL')

and generate a tree node :

  >>> from zope.app.tree.node import Node
  >>> node = Node(ns)

We can now ask the menu for the title of the namespace

  >>> menu.getMenuTitle(node)
  'All Namespaces'

and the link to the namespace overview.

  >>> menu.getMenuLink(node) is None
  True

Since the 'ALL' namespace is not that useful, let's create a namespace
instance for the browser namespace:

  >>> ns = Namespace(module, 'http://namespaces.zope.org/browser')
  >>> node = Node(ns)

And again we can get its title and menu link:

  >>> menu.getMenuTitle(node)
  'browser'
  >>> menu.getMenuLink(node) is None
  True

Now we add the ``page`` directive to the browser namespace:

  >>> from zope.app.apidoc.zcmlmodule import Directive
  >>> dir = Directive(ns, 'page', None, None, None, None)
  >>> node = Node(dir)

And we can get its menu title and link.

  >>> menu.getMenuTitle(node)
  'page'
  >>> menu.getMenuLink(node)
  'http://127.0.0.1/++apidoc++/ZCML/http_co__sl__sl_namespaces.zope.org_sl_browser/page/index.html'

Note that the directive's namespace URL is encoded, so it can be used in a
URL.


:class:`DirectiveDetails`
=========================

A browser view class that provides support for the ZCML directive overview.

Let's create a directive that we can use as context for the details:

  >>> from zope.interface import Interface, Attribute
  >>> class IFoo(Interface):
  ...     class_ = Attribute('class_')

  >>> def foo():
  ...     pass

  >>> directive = Directive(ns, 'page', IFoo, foo, None, ())

Now we can isntantiate the view:

  >>> from zope.app.apidoc.zcmlmodule.browser import DirectiveDetails

  >>> details = DirectiveDetails()
  >>> details.context = directive
  >>> details.request = TestRequest()

We are now ready to see what the details class has to offer.


:meth:`DirectiveDetails.getSchema`
----------------------------------

Returns the interface details class for the schema.

  >>> iface_details = details.getSchema()

  >>> iface_details
  <zope.app.apidoc.ifacemodule.browser.InterfaceDetails object at ...>

  >>> iface_details.context
  <InterfaceClass builtins.IFoo>

The :meth:`DirectiveDetails._getFieldName` method of the interface details has been overridden to
neglect trailing underscores in the field name. This is necessary, since
Python keywords cannot be used as field names:

  >>> iface_details._getFieldName(IFoo['class_'])
  'class'


:meth:`DirectiveDetails.getNamespaceName`
-----------------------------------------

Return the name of the namespace.

  >>> details.getNamespaceName()
  'http://namespaces.zope.org/browser'

If the directive is in the 'ALL' namespace, a special string is returned:

  >>> details2 = DirectiveDetails()
  >>> ns2 = Namespace(module, 'ALL')
  >>> details2.context = Directive(ns2, 'include', None, None, None, None)

  >>> details2.getNamespaceName()
  '<i>all namespaces</i>'


:meth:`getFileInfo`
-------------------

Get the file where the directive was declared. If the info attribute is not
set, return ``None``:

  >>> details.getFileInfo() is None
  True

If the info attribute is a parser info, then return the details:

  >>> from zope.configuration.xmlconfig import ParserInfo
  >>> details.context.info = ParserInfo('foo.zcml', 2, 3)
  >>> info = details.getFileInfo()
  >>> from pprint import pprint
  >>> pprint(info, width=1)
  {'column': 3,
   'ecolumn': 3,
   'eline': 2,
   'file': 'foo.zcml',
   'line': 2}

If the info is a string, ``None`` should be returned again:

  >>> details.context.info = 'info here'
  >>> details.getFileInfo() is None
  True


:meth:`DirectiveDetails.getInfo`
--------------------------------

Get the configuration information string of the directive:

  >>> details.context.info = 'info here'
  >>> details.getInfo()
  'info here'

Return ``None``, if the info attribute is a parser info:

  >>> details.context.info = ParserInfo('foo.zcml', 2, 3)
  >>> details.getInfo() is None
  True


:meth:`DirectiveDetails.getHandler`
-----------------------------------

Return information about the directive handler object.

  >>> pprint(details.getHandler(), width=1)
  {'path': 'None.foo',
   'url': None}


:meth:`DirectiveDetails.getSubdirectives`
-----------------------------------------

Create a list of subdirectives. Currently, we have not specifiedany
subdirectives

  >>> details.getSubdirectives()
  []

but if we add one

  >>> def handler():
  ...     pass

  >>> details.context.subdirs = (
  ...     ('browser', 'foo', IFoo, handler, 'info'),)

the result becomes more interesting:

  >>> pprint(details.getSubdirectives(), width=1)
  [{'handler': {'path': 'None.handler', 'url': None},
    'info': 'info',
    'name': 'foo',
    'namespace': 'browser',
    'schema': <zope.app.apidoc.ifacemodule.browser.InterfaceDetails ...>}]
