=========================
 Miscellaneous Utilities
=========================

.. currentmodule:: zope.app.apidoc.utilities

The utilities module provides some useful helper functions and classes that
make the work of the API doctool and inspection code easier.

  >>> from zope.app.apidoc import utilities


:func:`relativizePath`
======================

When dealing with files, such as page templates and text files, and not with
Python paths, it is necessary to keep track of the the absolute path of the
file. However, for presentation purposes, the absolute path is inappropriate
and we are commonly interested in the path starting at the Zope 3 root
directory. This function attempts to remove the absolute path to the root
directory and replaces it with "Zope3".

  >>> import os
  >>> path = os.path.join(os.path.dirname(utilities.__file__), 'README.txt')

  >>> path = utilities.relativizePath(path)
  >>> path.replace('\\', '/') # Be kind to Windows users
  'Zope3/zope/app/apidoc/README.txt'

If the base path is not found in a particular path, the original path is
returned:

  >>> otherpath = 'foo/bar/blah.txt'
  >>> utilities.relativizePath(otherpath)
  'foo/bar/blah.txt'


:func:`truncateSysPath`
=========================

In some cases it is useful to just know the path after the sys path of a
module. For example, you have a path of a file in a module. To look up the
module, the simplest to do is to retrieve the module path and look into the
system's modules list.

  >>> import sys
  >>> sysBase = sys.path[0]

  >>> utilities.truncateSysPath(sysBase + '/some/module/path')
  'some/module/path'

If there is no matching system path, then the whole path is returned:

  >>> utilities.truncateSysPath('some/other/path')
  'some/other/path'


:class:`ReadContainerBase`
==========================

This class serves as a base class for
:class:`zope.container.interfaces.IReadContainer` objects that
minimizes the implementation of an ``IReadContainer`` to two methods,
``get()`` and ``items()``, since the other methods can be implemented
using these two.

Note that this implementation might be very expensive for certain container,
especially if collecting the items is of high order. However, there are many
scenarios when one has a complete mapping already and simply want to persent
it as an ``IReadContainer``.

Let's start by making a simple ``IReadContainer`` implementation using the
class:

  >>> class Container(utilities.ReadContainerBase):
  ...     def get(self, key, default=None):
  ...         return {'a': 1, 'b': 2}.get(key, default)
  ...     def items(self):
  ...         return [('a', 1), ('b', 2)]

  >>> container = Container()

Now we can use the methods. First ``get()``

  >>> container.get('a')
  1
  >>> container.get('c') is None
  True
  >>> container['b']
  2

and then ``items()``

  >>> container.items()
  [('a', 1), ('b', 2)]
  >>> container.keys()
  ['a', 'b']
  >>> container.values()
  [1, 2]

Then naturally, all the other methods work as well:

  * ``__getitem__(key)``

    >>> container['a']
    1
    >>> container['c']
    Traceback (most recent call last):
    ...
    KeyError: 'c'

  * ``__contains__(key)``

    >>> 'a' in container
    True
    >>> 'c' in container
    False

  * ``keys()``

    >>> container.keys()
    ['a', 'b']

  * ``__iter__()``

    >>> iterator = iter(container)
    >>> next(iterator)
    1
    >>> next(iterator)
    2
    >>> next(iterator)
    Traceback (most recent call last):
    ...
    StopIteration

  * ``values()``

    >>> container.values()
    [1, 2]

  * ``__len__()``

    >>> len(container)
    2


:func:`getPythonPath`
=====================

Return the path of the object in standard Python dot-notation.

This function makes only sense for objects that provide a name, since we
cannot determine the path otherwise. Instances, for example, do not have a
``__name__`` attribute, so we would expect them to fail.

For interfaces we simply get

  >>> from zope.interface import Interface
  >>> class ISample(Interface):
  ...     pass

  >>> utilities.getPythonPath(ISample)
  'zope.app.apidoc.doctest.ISample'

and for classes we get the name of the class

  >>> class Sample(object):
  ...     def sample(self):
  ...         pass

  >>> utilities.getPythonPath(Sample)
  'zope.app.apidoc.doctest.Sample'

If a method is passed in, its class path is returned:

  >>> utilities.getPythonPath(Sample().sample)
  'zope.app.apidoc.doctest.Sample'
  >>> utilities.getPythonPath(Sample.sample)
  'zope.app.apidoc.doctest.Sample'

Plain functions are also supported:

  >>> def sample():
  ...     pass

  >>> utilities.getPythonPath(sample)
  'zope.app.apidoc.doctest.sample'

Modules are another kind of objects that can return a python path:

  >>> utilities.getPythonPath(utilities)
  'zope.app.apidoc.utilities'

Passing in ``None`` returns ``None``:

  >>> utilities.getPythonPath(None)

Clearly, instance lookups should fail:

  >>> utilities.getPythonPath(Sample())
  Traceback (most recent call last):
  ...
  AttributeError: 'Sample' object has no attribute '__name__'...


:func:`isReferencable`
======================

Determine whether a path can be referenced in the API doc, usually by the code
browser module. Initially you might think that all objects that have paths can
be referenced somehow. But that's not true, partially by design of apidoc, but
also due to limitations of the Python language itself.

First, here are some cases that work:

  >>> utilities.isReferencable('zope')
  True
  >>> utilities.isReferencable('zope.app')
  True
  >>> utilities.isReferencable('zope.app.apidoc.apidoc.APIDocumentation')
  True
  >>> utilities.isReferencable('zope.app.apidoc.apidoc.handleNamespace')
  True

The first case is ``None``. When you ask for the python path of ``None``, you
get ``None``, so that result should not be referencable:

  >>> utilities.isReferencable(None)
  False

By design we also do not document any private classes and functions:

  >>> utilities.isReferencable('some.path.to._Private')
  False
  >>> utilities.isReferencable('some.path.to.__Protected')
  False
  >>> utilities.isReferencable('zope.app.apidoc.__doc__')
  True

Some objects might fake their module name, so that it does not exist:

  >>> utilities.isReferencable('foo.bar')
  False

On the other hand, you might have a valid module, but non-existent attribute:

  >>> utilities.isReferencable('zope.app.apidoc.MyClass')
  False

Note that this case is also used for types that are generated using the
``type()`` function:

  >>> mytype = type('MyType', (object,), {})
  >>> path = utilities.getPythonPath(mytype)
  >>> path
  'zope.app.apidoc.doctest.MyType'

  >>> utilities.isReferencable(path)
  False

Next, since API doc does not allow the documentation of instances yet, it
is not possible to document singletons, so they are not referencable:

  >>> class Singelton(object):
  ...     pass

  >>> utilities.isReferencable('zope.app.apidoc.doctest.Singelton')
  True

  >>> Singelton = Singelton()

  >>> utilities.isReferencable('zope.app.apidoc.doctest.Singelton')
  False

Finally, the global ``IGNORE_MODULES`` list from the class registry is also
used to give a negative answer. If a module is listed in ``IGNORE_MODULES``,
then ``False`` is returned.

  >>> from zope.app.apidoc import classregistry
  >>> classregistry.IGNORE_MODULES.append('zope.app.apidoc')

  >>> utilities.isReferencable('zope.app')
  True
  >>> utilities.isReferencable('zope.app.apidoc')
  False
  >>> utilities.isReferencable('zope.app.apidoc.apidoc.APIDocumentation')
  False

  >>> classregistry.IGNORE_MODULES.pop()
  'zope.app.apidoc'
  >>> utilities.isReferencable('zope.app.apidoc')
  True


:func:`getPermissionIds`
========================

Get the permissions of a class attribute. The attribute is specified by name.

Either the ``klass`` or the ``checker`` argument must be specified. If the class
is specified, then the checker for it is looked up. Furthermore, this function
only works with ``INameBasedChecker`` checkers. If another checker is found,
``None`` is returned for the permissions.

We start out by defining the class and then the checker for it:

  >>> from zope.security.checker import Checker, defineChecker
  >>> from zope.security.checker import CheckerPublic

  >>> class Sample(object):
  ...     attr = 'value'
  ...     attr3 = 'value3'

  >>> class Sample2(object):
  ...      pass

  >>> checker = Checker({'attr': 'zope.Read', 'attr3': CheckerPublic},
  ...                   {'attr': 'zope.Write', 'attr3': CheckerPublic})
  >>> defineChecker(Sample, checker)

Now let's see how this function works:

  >>> entries = utilities.getPermissionIds('attr', klass=Sample)
  >>> entries['read_perm']
  'zope.Read'
  >>> entries['write_perm']
  'zope.Write'

  >>> from zope.security.checker import getCheckerForInstancesOf
  >>> entries = utilities.getPermissionIds('attr',
  ...                                      getCheckerForInstancesOf(Sample))
  >>> entries['read_perm']
  'zope.Read'
  >>> entries['write_perm']
  'zope.Write'

The ``Sample`` class does not know about the ``attr2`` attribute:

  >>> entries = utilities.getPermissionIds('attr2', klass=Sample)
  >>> print(entries['read_perm'])
  n/a
  >>> print(entries['write_perm'])
  n/a

The ``Sample2`` class does not have a checker:

  >>> entries = utilities.getPermissionIds('attr', klass=Sample2)
  >>> entries['read_perm'] is None
  True
  >>> entries['write_perm'] is None
  True

Finally, the ``Sample`` class' ``attr3`` attribute is public:

  >>> entries = utilities.getPermissionIds('attr3', klass=Sample)
  >>> print(entries['read_perm'])
  zope.Public
  >>> print(entries['write_perm'])
  zope.Public


:func:`getFunctionSignature`
============================

Return the signature of a function or method. The ``func`` argument *must* be a
generic function or a method of a class.

First, we get the signature of a function that has a specific positional and
keyword argument:

  >>> def func(attr, attr2=None):
  ...     pass
  >>> utilities.getFunctionSignature(func)
  '(attr, attr2=None)'

Here is a function that has an unspecified amount of keyword arguments:

  >>> def func(attr, **kw):
  ...     pass
  >>> utilities.getFunctionSignature(func)
  '(attr, **kw)'

And here we mix specified and unspecified keyword arguments:

  >>> def func(attr, attr2=None, **kw):
  ...     pass
  >>> utilities.getFunctionSignature(func)
  '(attr, attr2=None, **kw)'

In the next example we have unspecified positional and keyword arguments:

  >>> def func(*args, **kw):
  ...     pass
  >>> utilities.getFunctionSignature(func)
  '(*args, **kw)'

And finally an example, where we have on unspecified keyword arguments without
any positional arguments:

  >>> def func(**kw):
  ...     pass
  >>> utilities.getFunctionSignature(func)
  '(**kw)'

Next we test whether the signature is correctly determined for class
methods. Note that the ``self`` argument is removed from the signature, since it
is not essential for documentation:

We start out with a simple positional argument:

  >>> class Klass(object):
  ...     def func(self, attr):
  ...         pass
  >>> utilities.getFunctionSignature(Klass.func, ignore_self=True)
  '(attr)'
  >>> utilities.getFunctionSignature(Klass().func)
  '(attr)'

Next we have specific and unspecified positional arguments as well as
unspecified keyword arguments:

  >>> class Klass(object):
  ...     def func(self, attr, *args, **kw):
  ...         pass
  >>> utilities.getFunctionSignature(Klass().func, ignore_self=True)
  '(attr, *args, **kw)'
  >>> utilities.getFunctionSignature(Klass().func)
  '(attr, *args, **kw)'

If you do not pass a function or method to the function, it will fail:

  >>> utilities.getFunctionSignature('func')
  Traceback (most recent call last):
  ...
  TypeError: func must be a function or method not a ...

However, lists of this type are not allowed inside the argument list::

  >>> def func([arg1, arg2]):
  ...     pass
  Traceback (most recent call last):
  ...
  SyntaxError: invalid syntax...

Internal assignment is also not legal::

  >>> def func((arg1, arg2=1)):
  ...     pass
  Traceback (most recent call last):
  ...
  SyntaxError: invalid syntax...


:func:`getPublicAttributes`
===========================

Return a list of public attribute names for a given object.

This excludes any attribute starting with '_', which includes attributes of
the form ``__attr__``, which are commonly considered public, but they are so
special that they are excluded. The ``obj`` argument can be either a classic
class, type or instance of the previous two. Note that the term "attributes"
here includes methods and properties.

First we need to create a class with some attributes, properties and methods:

  >>> class Nonattr(object):
  ...     def __get__(*a):
  ...         raise AttributeError('nonattr')

  >>> class Sample(object):
  ...     attr = None
  ...     def __str__(self):
  ...         return ''
  ...     def func(self):
  ...         pass
  ...     def _getAttr(self):
  ...         return self.attr
  ...     attr2 = property(_getAttr)
  ...
  ...     nonattr = Nonattr() # Should not show up in public attrs

We can simply pass in the class and get the public attributes:

  >>> attrs = utilities.getPublicAttributes(Sample)
  >>> attrs.sort()
  >>> attrs
  ['attr', 'attr2', 'func']

Note that we exclude attributes that would raise attribute errors,
like our silly Nonattr.

But an instance of that class will work as well.

  >>> attrs = utilities.getPublicAttributes(Sample())
  >>> attrs.sort()
  >>> attrs
  ['attr', 'attr2', 'func']

The function will also take inheritance into account and return all inherited
attributes as well:

  >>> class Sample2(Sample):
  ...     attr3 = None

  >>> attrs = utilities.getPublicAttributes(Sample2)
  >>> attrs.sort()
  >>> attrs
  ['attr', 'attr2', 'attr3', 'func']


:func:`getInterfaceForAttribute`
================================

Determine the interface in which an attribute is defined. This function is
nice, if you have an attribute name which you retrieved from a class and want
to know which interface requires it to be there.

Either the ``interfaces`` or ``klass`` argument must be specified. If ``interfaces``
is not specified, the ``klass`` is used to retrieve a list of
interfaces. ``interfaces`` must be iterable.

``asPath`` specifies whether the dotted name of the interface or the interface
object is returned.

First, we need to create some interfaces and a class that implements them:

  >>> from zope.interface import Interface, Attribute, implementer
  >>> class I1(Interface):
  ...     attr = Attribute('attr')

  >>> class I2(I1):
  ...     def getAttr():
  ...         '''get attr'''

  >>> @implementer(I2)
  ... class Sample(object):
  ...    pass

First we check whether an aatribute can be found in a list of interfaces:

  >>> utilities.getInterfaceForAttribute('attr', (I1, I2), asPath=False)
  <InterfaceClass zope.app.apidoc.doctest.I1>
  >>> utilities.getInterfaceForAttribute('getAttr', (I1, I2), asPath=False)
  <InterfaceClass zope.app.apidoc.doctest.I2>

Now we are repeating the same lookup, but using the class, instead of a list
of interfaces:

  >>> utilities.getInterfaceForAttribute('attr', klass=Sample, asPath=False)
  <InterfaceClass zope.app.apidoc.doctest.I1>
  >>> utilities.getInterfaceForAttribute('getAttr', klass=Sample, asPath=False)
  <InterfaceClass zope.app.apidoc.doctest.I2>

By default, ``asPath`` is ``True``, which means the path of the interface is
returned:

  >>> utilities.getInterfaceForAttribute('attr', (I1, I2))
  'zope.app.apidoc.doctest.I1'

If no match is found, ``None`` is returned.

  >>> utilities.getInterfaceForAttribute('attr2', (I1, I2)) is None
  True
  >>> utilities.getInterfaceForAttribute('attr2', klass=Sample) is None
  True

If both, the ``interfaces`` and ``klass`` argument are missing, raise an error:

  >>> utilities.getInterfaceForAttribute('getAttr')
  Traceback (most recent call last):
  ...
  ValueError: need to specify interfaces or klass

Similarly, it does not make sense if both are specified:

  >>> utilities.getInterfaceForAttribute('getAttr', interfaces=(I1,I2),
  ...                                    klass=Sample)
  Traceback (most recent call last):
  ...
  ValueError: must specify only one of interfaces and klass


:func:`columnize`
=================

This function places a list of entries into columns.

Here are some examples:

  >>> utilities.columnize([1], 3)
  [[1]]

  >>> utilities.columnize([1, 2], 3)
  [[1], [2]]

  >>> utilities.columnize([1, 2, 3], 3)
  [[1], [2], [3]]

  >>> utilities.columnize([1, 2, 3, 4], 3)
  [[1, 2], [3], [4]]

  >>> utilities.columnize([1], 2)
  [[1]]

  >>> utilities.columnize([1, 2], 2)
  [[1], [2]]

  >>> utilities.columnize([1, 2, 3], 2)
  [[1, 2], [3]]

  >>> utilities.columnize([1, 2, 3, 4], 2)
  [[1, 2], [3, 4]]


:func:`getDocFormat`
====================

This function inspects a module to determine the supported documentation
format. The function returns a valid renderer source factory id.

If the ``__docformat__`` module attribute is specified, its value will be used
to look up the factory id:

  >>> from zope.app.apidoc import apidoc
  >>> utilities.getDocFormat(apidoc)
  'zope.source.rest'

By default restructured text is returned:

  >>> utilities.getDocFormat(object())
  'zope.source.rest'

This is a sensible default since much documentation is now written
with Sphinx in mind (which of course defaults to rendering
restructured text). As long as docutils' error reporting level is set
sufficiently high (``severe``), unknown Sphinx directives and slightly
malformed markup do not produce error messages, either on the console
or in the generated HTML.

The ``__docformat__`` attribute can also optionally specify a language field. We
simply ignore it:

  >>> class Module(object):
  ...     pass
  >>> module = Module()
  >>> module.__docformat__ = 'structuredtext en'
  >>> utilities.getDocFormat(module)
  'zope.source.stx'


:func:`dedentString`
====================

Before doc strings can be processed using STX or ReST they must be dendented,
since otherwise the output will be incorrect. Let's have a look at some
docstrings and see how they are correctly dedented.

Let's start with a simple one liner. Nothing should happen:

  >>> def func():
  ...     '''One line documentation string'''

  >>> utilities.dedentString(func.__doc__)
  'One line documentation string'

Now what about one line docstrings that start on the second line? While this
format is discouraged, it is frequently used:

  >>> def func():
  ...     '''
  ...     One line documentation string
  ...     '''

  >>> utilities.dedentString(func.__doc__)
  '\nOne line documentation string\n'

We can see that the leading whitespace on the string is removed, but not the
newline character. Let's now try a simple multi-line docstring:

  >>> def func():
  ...     '''Short description
  ...
  ...     Lengthy description, giving some more background information and
  ...     discuss some edge cases.
  ...     '''

  >>> print(utilities.dedentString(func.__doc__))
  Short description
  <BLANKLINE>
  Lengthy description, giving some more background information and
  discuss some edge cases.
  <BLANKLINE>

Again, the whitespace was removed only after the first line. Also note that
the function determines the indentation level correctly. So what happens if
there are multiple indentation levels? The smallest amount of indentation is
chosen:

  >>> def func():
  ...     '''Short description
  ...
  ...     Root Level
  ...
  ...       Second Level
  ...     '''

  >>> print(utilities.dedentString(func.__doc__))
  Short description
  <BLANKLINE>
  Root Level
  <BLANKLINE>
    Second Level
  <BLANKLINE>

  >>> def func():
  ...     '''Short description
  ...
  ...       $$$ print 'example'
  ...       example
  ...
  ...     And now the description.
  ...     '''

  >>> print(utilities.dedentString(func.__doc__))
  Short description
  <BLANKLINE>
    $$$ print 'example'
    example
  <BLANKLINE>
  And now the description.
  <BLANKLINE>


:func:`renderText`
==================

A function that quickly renders the given text using the specified format.

If the ``module`` argument is specified, the function will try to determine the
format using the module. If the ``format`` argument is given, it is simply
used. Clearly, you cannot specify both, the ``module`` and ``format`` argument.

You specify the format as follows:

  >>> utilities.renderText(u'Hello!\n', format='zope.source.rest')
  '<p>Hello!</p>\n'

Note that the format string must be a valid source factory id; if the factory
id is not given, 'zope.source.stx' is used. Thus, specifying the module is
often safer (if available):

  >>> utilities.renderText(u'Hello!\n', module=apidoc)
  '<p>Hello!</p>\n'

Byte input is accepted, so long as it can be decoded:

  >>> utilities.renderText(b'Hello!\n', module=apidoc)
  '<p>Hello!</p>\n'
