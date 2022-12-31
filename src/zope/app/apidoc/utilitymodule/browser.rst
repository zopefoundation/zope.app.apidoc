==================================
 Utilities Menu and Details Views
==================================

.. currentmodule:: zope.app.apidoc.utilitymodule.browser

:class:`Menu`
=============

This is a class that helps building the menu. The ``menu_macros`` expect the menu
view class to have the :meth:`Menu.getMenuTitle` and :meth:`Menu.getMenuLink` methods
implemented. ``node`` is a :class:`zope.app.tree.node.Node` instance.

Let's start by creating the menu:

  >>> from zope.app.apidoc.utilitymodule.browser import Menu
  >>> menu = Menu()

then we need a Utility module instance and add context and request to menu:

  >>> from zope.publisher.browser import TestRequest
  >>> module = apidoc.get('Utility')
  >>> request = TestRequest()
  >>> menu.context = module
  >>> menu.request = request

Now we want to get the menu title and link for a utility interface. To do that
we first have to create a utility interface

  >>> from zope.app.apidoc.tests import Root
  >>> from zope.app.apidoc.utilitymodule.utilitymodule import UtilityInterface
  >>> uiface = UtilityInterface(Root(), 'foo.bar.iface', None)

and then wrap it in a node:

  >>> from zope.app.tree.node import Node
  >>> node = Node(uiface)

You can now get the title and link from the menu:

  >>> menu.getMenuTitle(node)
  'iface'
  >>> menu.getMenuLink(node)
  'http://127.0.0.1/++apidoc++/Interface/foo.bar.iface/index.html'

Next, let's get the menu title and link for a utility with a name. We first
have to create a utility registration

  >>> foobar_reg = type(
  ...     'RegistrationStub', (),
  ...     {'name': 'FooBar', 'provided': None,
  ...      'component': None, 'info': ''})()

which is then wrapped in a
:class:`~zope.app.apidoc.utilitymodule.utilitymodule.Utility`
documentation class and then in a node:

  >>> from zope.app.apidoc.utilitymodule.utilitymodule import Utility
  >>> util = Utility(uiface, foobar_reg)
  >>> node = Node(util)

We can now ask the menu to give us the tile and link for the utility:

  >>> menu.getMenuTitle(node)
  'FooBar'
  >>> menu.getMenuLink(node)
  'http://127.0.0.1/++apidoc++/Utility/foo.bar.iface/Rm9vQmFy/index.html'

Finally, we get menu title and link for a utility without a name:

  >>> from zope.app.apidoc.utilitymodule.utilitymodule import NONAME
  >>> noname_reg = type(
  ...     'RegistrationStub', (),
  ...     {'name': NONAME, 'provided': None,
  ...      'component': None, 'info': ''})()

  >>> util = Utility(uiface, noname_reg)
  >>> node = Node(util)
  >>> menu.getMenuTitle(node)
  'no name'
  >>> menu.getMenuLink(node)
  'http://127.0.0.1/++apidoc++/Utility/foo.bar.iface/X19ub25hbWVfXw==/index.html'


:class:`UtilityDetails`
=======================

This class provides presentation-ready data about a particular utility.

:meth:`UtilityDetails.getName`
------------------------------

Get the name of the utility.

  >>> from zope.app.apidoc.utilitymodule.browser import UtilityDetails
  >>> details = UtilityDetails()
  >>> details.context = Utility(None, foobar_reg)
  >>> details.getName()
  'FooBar'

Return the string ``no name``, if the utility has no name.

  >>> details.context = Utility(None, noname_reg)
  >>> details.getName()
  'no name'


:meth:`UtilityDetails.getInterface`
-----------------------------------

Return the interface details view for the interface the utility provides.

Let's start by creating the utility interface and building a utility
registration:

  >>> from zope.interface import Interface
  >>> class IBlah(Interface):
  ...     pass

  >>> blah_reg = type(
  ...     'RegistrationStub', (),
  ...     {'name': 'Blah', 'provided': IBlah,
  ...      'component': None, 'info': ''})()

Then we wrap the registration in the utility documentation class and create
the details view:

  >>> details = UtilityDetails()
  >>> details.context = Utility(None, blah_reg)
  >>> details.request = None

Now that we have the details view, we can look up the interface's detail view
and get the id (for example):

  >>> iface = details.getInterface()
  >>> iface.getId()
  'builtins.IBlah'


:meth:`UtilityDetails.getComponent`
-----------------------------------

Return the Python path and a code browser URL path of the implementation
class.

This time around we create the utility class and put it into a utility
registration:

  >>> class Foo(object):
  ...     pass

  >>> foo_reg = type(
  ...     'RegistrationStub', (),
  ...     {'name': '', 'provided': Interface, 'component': Foo(), 'info': ''})()

Then we create a utility documentation class and its details view:

  >>> details = UtilityDetails()
  >>> details.context = Utility(Interface, foo_reg)

Now we can get the component information:

  >>> from pprint import pprint
  >>> pprint(details.getComponent(), width=1)
  {'path': 'builtins.Foo', 'url': None}
