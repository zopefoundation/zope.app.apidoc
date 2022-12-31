========================================
 Module Menu and ZCML Directive Details
========================================

This document provides an overview of all browser-presentation related
objects.

.. currentmodule:: zope.app.apidoc.ifacemodule

:func:`menu.getAllTextOfInterface`
==================================

Get all searchable text from an interface

  >>> import zope.interface
  >>> import zope.schema
  >>> class IFoo(zope.interface.Interface):
  ...     '''foo'''
  ...
  ...     def bar(self):
  ...         '''bar'''
  ...
  ...     blah = zope.interface.Attribute('blah', 'blah')
  ...
  ...     field = zope.schema.Field(
  ...         title = 'title', description = 'description')

Now get the text. Note that there is no particular order during the text
collection.

  >>> from zope.app.apidoc.ifacemodule.menu import getAllTextOfInterface
  >>> text = getAllTextOfInterface(IFoo)
  >>> 'foo' in text
  True
  >>> 'bar' in text
  True
  >>> 'blah' in text
  True
  >>> 'field' in text
  True
  >>> 'title' in text
  True
  >>> 'description' in text
  True


``Menu`` class
==============

This is the :class:`menu class <menu.Menu>` for the Interface
Documentation Module.

The menu allows one to look for interfaces by full-text search or
partial names. The :meth:`findInterfaces <menu.Menu.findInterfaces>`
method provides a simple search mechanism.

Before we can test the method, let's create a :class:`menu.Menu`
instance:

  >>> from zope.interface.interfaces import IElement, IAttribute

  >>> from zope.app.apidoc.ifacemodule.menu import Menu
  >>> menu = Menu()
  >>> menu.context = {'IElement': IElement, 'IAttribute': IAttribute}
  >>> menu.request = {'name_only': 'on', 'search_str': ''}

Now let's see how successful our searches are:

  >>> menu.request['search_str'] = 'Elem'
  >>> from pprint import pprint
  >>> pprint(menu.findInterfaces(), width=1)
  [{'name': 'IElement',
    'url': './IElement/index.html'}]

  >>> menu.request['search_str'] = 'I'
  >>> pprint(menu.findInterfaces(), width=1)
  [{'name': 'IAttribute',
    'url': './IAttribute/index.html'},
   {'name': 'IElement',
    'url': './IElement/index.html'}]

Now using the full text search:

  >>> del menu.request['name_only']

  >>> menu.request['search_str'] = 'object'
  >>> pprint(menu.findInterfaces(), width=1)
  [{'name': 'IAttribute',
    'url': './IAttribute/index.html'},
   {'name': 'IElement',
    'url': './IElement/index.html'}]

  >>> menu.request['search_str'] = 'Stores'
  >>> pprint(menu.findInterfaces(), width=1)
  [{'name': 'IAttribute',
    'url': './IAttribute/index.html'}]


``InterfaceDetails`` class
==========================
.. currentmodule:: zope.app.apidoc.ifacemodule.browser

:class:`This view <InterfaceDetails>` provides many details
about an interface. Most methods of the class actually use the public
inspection API.

Before we can test the view, we need to create an interesting setup, so that
the view can provide some useful data. Let's start by defining a complex
interface:

  >>> class IFoo(zope.interface.Interface):
  ...     """This is the Foo interface
  ...
  ...     More description here...
  ...     """
  ...     foo = zope.interface.Attribute('This is foo.')
  ...     bar = zope.interface.Attribute('This is bar.')
  ...
  ...     title = zope.schema.TextLine(
  ...         description='Title',
  ...         required=True,
  ...         default='Foo')
  ...
  ...     description = zope.schema.Text(
  ...         description='Desc',
  ...         required=False,
  ...         default='Foo.')
  ...
  ...     def blah():
  ...         """This is blah."""
  ...
  ...     def get(key, default=None):
  ...         """This is get."""

Let's now create another interface ``IBar`` and make ``Foo`` an adapter from
``IBar`` to ``IFoo``:

  >>> class IBar(zope.interface.Interface):
  ...     pass

  >>> @zope.interface.implementer(IFoo)
  ... class Foo(object):
  ...     pass

  >>> from zope import component as ztapi
  >>> ztapi.provideAdapter(adapts=(IBar,), provides=IFoo, factory=Foo)

  >>> from zope.app.apidoc.classregistry import classRegistry
  >>> classRegistry['builtins.Foo'] = Foo

Let's also register a factory for ``Foo``

  >>> from zope.component.interfaces import IFactory
  >>> from zope.component.factory import Factory
  >>> ztapi.provideUtility(Factory(Foo, title='Foo Factory'), IFactory,
  ...                      'FooFactory')

and a utility providing ``IFoo``:

  >>> ztapi.provideUtility(Foo(), IFoo, 'The Foo')

Now that the initial setup is done, we can create an interface that is located
in the interface documentation module

  >>> ifacemodule = apidoc.get('Interface')
  >>> from zope.location import LocationProxy
  >>> iface = LocationProxy(IFoo, ifacemodule, 'IFoo')

and finally the details view:

  >>> from zope.publisher.browser import TestRequest
  >>> from zope.app.apidoc.ifacemodule.browser import InterfaceDetails
  >>> details = InterfaceDetails(iface, TestRequest())


:meth:`InterfaceDetails.getId`
------------------------------

Return the id of the field as it is defined for the interface
utility.

  >>> details.getId()
  'IFoo'

:meth:`InterfaceDetails.getDoc`
-------------------------------

Return the main documentation string of the interface.

  >>> details.getDoc()[:32]
  '<p>This is the Foo interface</p>'


:meth:`InterfaceDetails.getBases`
---------------------------------

Get all bases of this class

  >>> details.getBases()
  ['zope.interface.Interface']


:meth:`InterfaceDetails.getTypes`
---------------------------------

Return a list of interface types that are specified for this interface.

Initially we do not have any types

  >>> details.getTypes()
  []

but when I create and assign a type to the interface

  >>> class IMyType(zope.interface.interfaces.IInterface):
  ...     pass

  >>> zope.interface.directlyProvides(IFoo, IMyType)

we get a result:

  >>> pprint(details.getTypes(), width=1)
  [{'name': 'IMyType',
    'path': 'builtins.IMyType'}]


:meth:`InterfaceDetails.getAttributes`
--------------------------------------

Return a list of attributes in the order they were specified.

  >>> pprint(sorted(details.getAttributes(), key=lambda x: x['name']))
  [{'doc': '<p>This is bar.</p>\n',
    'name': 'bar'},
   {'doc': '<p>This is foo.</p>\n',
    'name': 'foo'}]


:meth:`InterfaceDetails.getMethods`
-----------------------------------

Return a list of methods in the order they were specified.

  >>> pprint(sorted(details.getMethods(), key=lambda x: x['name']))
  [{'doc': '<p>This is blah.</p>\n',
    'name': 'blah',
    'signature': '()'},
   {'doc': '<p>This is get.</p>\n',
    'name': 'get',
    'signature': '(key, default=None)'}]


:meth:`InterfaceDetails.getFields`
----------------------------------

Return a list of fields in required + alphabetical order.

The required attributes are listed first, then the optional attributes.

  >>> pprint(details.getFields(), width=1)
  [{'class': {'name': 'TextLine',
              'path': 'zope/schema/_bootstrapfields/TextLine'},
    'default': "'Foo'",
    'description': '<p>Title</p>\n',
    'iface': {'id': 'zope.schema.interfaces.ITextLine',
              'name': 'ITextLine'},
    'name': 'title',
    'required': True,
    'required_string': 'required',
    'title': ''},
   {'class': {'name': 'Text',
              'path': 'zope/schema/_bootstrapfields/Text'},
    'default': "'Foo.'",
    'description': '<p>Desc</p>\n',
    'iface': {'id': 'zope.schema.interfaces.IText',
              'name': 'IText'},
    'name': 'description',
    'required': False,
    'required_string': 'optional',
    'title': ''}]

:meth:`InterfaceDetails.getSpecificRequiredAdapters`
----------------------------------------------------

Get adapters where this interface is required.

  >>> pprint(details.getSpecificRequiredAdapters())
  []

:meth:`InterfaceDetails.getExtendedRequiredAdapters`
----------------------------------------------------

Get adapters where this interface is required.

  >>> pprint(details.getExtendedRequiredAdapters())
  []

Note that this includes all interfaces registered for
:class:`zope.interface.interface.Interface`.


:meth:`InterfaceDetails.getGenericRequiredAdapters`
---------------------------------------------------

Get adapters where this interface is required.

  >>> required = details.getGenericRequiredAdapters()
  >>> len(required) >= 10
  True


:meth:`InterfaceDetails.getProvidedAdapters`
--------------------------------------------

Get adapters where this interface is provided.

  >>> pprint(details.getProvidedAdapters(), width=1)
  [{'doc': '',
    'factory': 'builtins.Foo',
    'factory_url': None,
    'name': '',
    'provided': {'module': 'builtins',
                 'name': 'IFoo'},
    'required': [{'isInterface': True,
                  'isType': False,
                  'module': 'builtins',
                  'name': 'IBar'}],
    'zcml': None}]



:meth:`InterfaceDetails.getClasses`
-----------------------------------

Get the classes that implement this interface.

  >>> pprint(details.getClasses(), width=1)
  [{'path': 'builtins.Foo',
    'url': 'builtins/Foo'}]

:meth:`InterfaceDetails.getFactories`
-------------------------------------

Return the factories, who will provide objects implementing this
interface.

  >>> pprint(details.getFactories())
  [{'description': '',
    'name': 'FooFactory',
    'title': 'Foo Factory',
    'url': None}]

:meth:`InterfaceDetails.getUtilities`
-------------------------------------

Return all utilities that provide this interface.

  >>> pprint(details.getUtilities())
  [{'iface_id': 'builtins.IFoo',
    'name': 'The Foo',
    'path': 'builtins.Foo',
    'url': None,
    'url_name': 'VGhlIEZvbw=='}]
