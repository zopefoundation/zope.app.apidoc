================================
 Interface Inspection Utilities
================================

.. currentmodule:: zope.app.apidoc.interface

This document is a presentation of the utility functions provided by

  >>> from zope.app.apidoc import interface

For the following demonstrations, we need a nice interface that we can inspect:

  >>> from zope.interface import Interface, Attribute
  >>> from zope.schema import Field, TextLine

  >>> class IFoo(Interface):
  ...     foo = Field(title=u"Foo")
  ...
  ...     bar = TextLine(title=u"Bar",
  ...                    description=u"The Bar",
  ...                    required=True,
  ...                    default=u"My Bar")
  ...
  ...     baz = Attribute('baz',
  ...                     'This is the baz attribute')
  ...
  ...     def blah(one, two, three=None, *args, **kwargs):
  ...         """This is the `blah` method."""


:func:`getElements`
===================

Return a dictionary containing all elements in an interface. The type
specifies whether we are looking for attributes, fields or methods. So let's
look at an example.

First, let's get the methods of an interface:

  >>> from zope.interface.interfaces import IMethod
  >>> sorted(interface.getElements(IFoo, type=IMethod).keys())
  ['blah']

and now the fields:

  >>> from zope.schema.interfaces import IField
  >>> names = sorted(interface.getElements(IFoo, type=IField).keys())
  >>> names
  ['bar', 'foo']

We can also get all attributes of course.

  >>> from zope.interface.interfaces import IAttribute
  >>> names = sorted(interface.getElements(IFoo, type=IAttribute).keys())
  >>> names
  ['bar', 'baz', 'blah', 'foo']

You might be surprised by the above result, since the fields and methods are
again included. However, fields and methods are just attributes and thus
extend the simple attribute implementation. If you want to get a list of
attributes that does not include fields and methods, see the
:func:`getAttributes` function.

The default type is :class:`zope.interface.interfaces.IElement` which
will simply return all elements of the interface:

  >>> names = sorted(interface.getElements(IFoo).keys())
  >>> names
  ['bar', 'baz', 'blah', 'foo']

Note: The interface you pass to this function *cannot* be proxied!
Presentation code often like to wrap interfaces in security proxies and apidoc
even uses location proxies for interface.


:func:`getFieldsInOrder`
========================

For presentation purposes we often want fields to have the a certain order,
most comonly the order they have in the interface. This function returns a
list of (name, field) tuples in a specified order.

The ``_itemkey`` argument provides the function that is used to extract
the key on which to order the fields. The default function, which
uses the fields' ``order`` attribute, should be the correct one for
99% of your needs.

Reusing the interface created above, we check the output:

  >>> [n for n, a in interface.getFieldsInOrder(IFoo)]
  ['foo', 'bar']

By changing the sort method to sort by names, we get:

  >>> [n for n, a in interface.getFieldsInOrder(
  ...       IFoo, _itemkey=lambda x: x[0])]
  ['bar', 'foo']


:func:`getAttributes`
=====================

This function returns a (name, attr) tuple for every attribute in the
interface. Note that this function will only return pure attributes; it
ignores methods and fields.

  >>> attrs = interface.getAttributes(IFoo)
  >>> attrs.sort()
  >>> attrs
  [('baz', <zope.interface.interface.Attribute object at ...>)]


:func:`getMethods`
==================

This function returns a (name, method) tuple for every declared method in the
interface.

  >>> methods = sorted(interface.getMethods(IFoo))
  >>> methods
  [('blah', <zope.interface.interface.Method object at ...>)]


:func:`getFields`
=================

This function returns a (name, field) tuple for every declared field in the
interface.

  >>> sorted(interface.getFields(IFoo))
  [('bar', <zope.schema._bootstrapfields.TextLine object at ...>),
   ('foo', <zope.schema._bootstrapfields.Field object at ...>)]

Note that this returns the same result as ``getFieldsInOrder()`` with the fields
sorted by their ``order`` attribute, except that you cannot specify the sort
function here. This function was mainly provided for symmetry with the other
functions.


:func:`getInterfaceTypes`
=========================

Interfaces can be categorized/grouped by using interface types. Interface
types simply extend :class:`zope.interface.interfaces.IInterface`, which are
basically meta-interfaces. The interface types are then provided by particular
interfaces.

The :func:`getInterfaceTypes` function returns a list of interface types that are
provided for the specified interface. Note that you commonly expect only one
type per interface, though.

Before we assign any type to our ``IFoo`` interface, there are no types
declared.

  >>> interface.getInterfaceTypes(IFoo)
  []

Now we define a new type called ``IContentType``

  >>> from zope.interface.interfaces import IInterface
  >>> class IContentType(IInterface):
  ...     pass

and have our interface provide it:

  >>> from zope.interface import directlyProvides
  >>> directlyProvides(IFoo, IContentType)

Note that ZCML has some more convenient methods of doing this. Now let's get
the interface types again:

  >>> interface.getInterfaceTypes(IFoo)
  [<InterfaceClass zope.app.apidoc.doctest.IContentType>]

Again note that the interface passed to this function *cannot* be proxied,
otherwise this method will pick up the proxy's interfaces as well.


:func:`getFieldInterface`
=========================

This function tries pretty hard to determine the best-matching interface that
represents the field. Commonly the field class has the same name as the field
interface (minus an "I"). So this is our first choice:

  >>> from zope.schema import Text, Int
  >>> interface.getFieldInterface(Text())
  <InterfaceClass zope.schema.interfaces.IText>

  >>> interface.getFieldInterface(Int())
  <InterfaceClass zope.schema.interfaces.IInt>

If the name matching method fails, it picks the first interface that extends
:class:`~.IField`:

  >>> from zope.schema.interfaces import IField
  >>> class ISpecialField(IField):
  ...     pass
  >>> class ISomething(Interface):
  ...     pass

  >>> from zope.interface import implementer
  >>> @implementer(ISomething, ISpecialField)
  ... class MyField:
  ...     pass

  >>> interface.getFieldInterface(MyField())
  <InterfaceClass zope.app.apidoc.doctest.ISpecialField>


:func:`getAttributeInfoDictionary`
==================================

This function returns a page-template-friendly dictionary for a simple
attribute:

  >>> from pprint import pprint
  >>> pprint(interface.getAttributeInfoDictionary(IFoo['baz']))
  {'doc': u'<p>This is the baz attribute</p>\n',
   'name': 'baz'}


:func:`getMethodInfoDictionary`
===============================

This function returns a page-template-friendly dictionary for a method:

  >>> pprint(interface.getMethodInfoDictionary(IFoo['blah'])) #doc
  {'doc':
     u'<p>This is the <cite>blah</cite> method.</p>\n',
   'name': 'blah',
   'signature': '(one, two, three=None, *args, **kwargs)'}


:func:`getFieldInfoDictionary`
==============================

This function returns a page-template-friendly dictionary for a field:

  >>> pprint(interface.getFieldInfoDictionary(IFoo['bar']), width=50)
  {'class': {'name': 'TextLine',
             'path': 'zope/schema/_bootstrapfields/TextLine'},
   'default': "u'My Bar'",
   'description': u'<p>The Bar</p>\n',
   'iface': {'id': 'zope.schema.interfaces.ITextLine',
             'name': 'ITextLine'},
   'name': 'bar',
   'required': True,
   'required_string': u'required',
   'title': u'Bar'}
