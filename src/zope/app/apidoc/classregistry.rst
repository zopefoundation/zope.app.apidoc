====================
 The Class Registry
====================

.. currentmodule:: zope.app.apidoc.classregistry

This :class:`little registry <ClassRegistry>` allows us to quickly
query a complete list of classes that are defined and used by Zope 3.
The prime feature of the class is the
:meth:`ClassRegistry.getClassesThatImplement` method that returns all
classes that implement the passed interface. Another method,
:meth:`ClassRegistry.getSubclassesOf` returns all registered
subclassess of the given class.

:class:`ClassRegistry`
======================

The class registry, subclassing the dictionary type, can be instantiated like
any other dictionary:

  >>> from zope.app.apidoc.classregistry import ClassRegistry
  >>> reg = ClassRegistry()

Let's now add a couple of classes to registry. The classes should implement
some interfaces, so that we can test all methods on the class registry:

  >>> from zope.interface import Interface, implementer

  >>> class IA(Interface):
  ...      pass
  >>> class IB(IA):
  ...      pass
  >>> class IC(Interface):
  ...      pass
  >>> class ID(Interface):
  ...      pass

  >>> @implementer(IA)
  ... class A(object):
  ...    pass
  >>> reg['A'] = A

  >>> @implementer(IB)
  ... class B:
  ...    pass
  >>> reg['B'] = B

  >>> @implementer(IC)
  ... class C(object):
  ...    pass
  >>> reg['C'] = C
  >>> class A2(A):
  ...    pass
  >>> reg['A2'] = A2

Since the registry is just a dictionary, we can ask for all its keys, which
are the names of the classes:

  >>> names = sorted(reg.keys())
  >>> names
  ['A', 'A2', 'B', 'C']

  >>> reg['A'] is A
  True

There are two API methods specific to the class registry:

:meth:`ClassRegistry.getClassesThatImplement`
---------------------------------------------

This method returns all classes that implement the specified interface:

  >>> from pprint import pprint
  >>> pprint(reg.getClassesThatImplement(IA))
  [('A', <class 'zope.app.apidoc.doctest.A'>),
   ('A2', <class 'zope.app.apidoc.doctest.A2'>),
   ('B', <class 'zope.app.apidoc.doctest.B'>)]

  >>> pprint(reg.getClassesThatImplement(IB))
  [('B', <class 'zope.app.apidoc.doctest.B'>)]

  >>> pprint(reg.getClassesThatImplement(IC))
  [('C', <class 'zope.app.apidoc.doctest.C'>)]

  >>> pprint(reg.getClassesThatImplement(ID))
  []

:meth:`ClassRegistry.getSubclassesOf`
-------------------------------------

This method will find all classes that inherit the specified class:

  >>> pprint(reg.getSubclassesOf(A))
  [('A2', <class '...A2'>)]

  >>> pprint(reg.getSubclassesOf(B))
  []


Safe Imports
============

Using the :func:`safe_import` function we can quickly look up modules by minimizing
import calls.

  >>> from zope.app.apidoc import classregistry
  >>> from zope.app.apidoc.classregistry import safe_import

First we try to find the path in ``sys.modules``, since this lookup is much
more efficient than importing it. If it was not found, we go back and try
to import the path. For security reasons, importing new modules is disabled by
default, unless the global ``__import_unknown_modules__`` variable is set to
true. If that also fails, we return the `default` value.

Here are some examples::

  >>> import sys
  >>> 'zope.app' in sys.modules
  True

  >>> safe_import('zope.app') is sys.modules['zope.app']
  True

  >>> safe_import('weirdname') is None
  True

For this example, we'll create a dummy module:

  >>> import os
  >>> import tempfile
  >>> dir = tempfile.mkdtemp()
  >>> filename = os.path.join(dir, 'testmodule.py')
  >>> sys.path.insert(0, dir)
  >>> with open(filename, 'w') as f:
  ...     _ = f.write('# dummy module\n')

The temporary module is not already imported:

  >>> module_name = 'testmodule'
  >>> module_name in sys.modules
  False

When we try ``safe_import()`` now, we will still get the `default` value,
because importing new modules is disabled by default:

  >>> safe_import(module_name) is None
  True

But once we activate the ``__import_unknown_modules__`` hook, the module
should be imported:

  >>> classregistry.__import_unknown_modules__ = True

  >>> safe_import(module_name).__name__ == module_name
  True
  >>> module_name in sys.modules
  True

Now clean up the temporary module, just to play nice:

  >>> del sys.modules[module_name]

Importing some code we cannot control, such as twisted, might raise errors
when imported without having a certain environment. In those cases, the safe
import should prevent the error from penetrating:

  >>> with open(os.path.join(dir, 'alwaysfail.py'), 'w') as f:
  ...     _ = f.write('raise ValueError\n')
  >>> sys.path.insert(0, dir)

  >>> safe_import('alwaysfail') is None
  True

Let's clean up the python path and temporary files:

  >>> del sys.path[0]
  >>> import shutil
  >>> shutil.rmtree(dir)

Another method to explicitely turning off the import of certain modules is to
declare that they should be ignored. For example, if we tell the class
registry to ignore ``zope.app``,

  >>> classregistry.IGNORE_MODULES.append('zope.app')

then we cannot import it anymore, even though we know it is available:

  >>> safe_import('zope.app') is None
  True

Note that all sub-packages are also unavailable:

  >>> safe_import('zope.app.apidoc') is None
  True

We also need to play nice concerning variables and have to reset the module
globals:

  >>> classregistry.IGNORE_MODULES.pop()
  'zope.app'
  >>> classregistry.__import_unknown_modules__ = False
