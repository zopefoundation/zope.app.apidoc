====================================
 The Utilities Documentation Module
====================================

.. currentmodule:: zope.app.apidoc.utilitymodule.utilitymodule

This documentation module organizes all registered utilities by their provided
interface and then by the name of the utility.

:class:`UtilityModule`
======================

This class represents the documentation of all utility interfaces. The
items of the container are all :class:`UtilityInterface` instances.

Let's start by creating a utility documentation module:

  >>> from zope.app.apidoc.utilitymodule.utilitymodule import UtilityModule
  >>> module = UtilityModule()

To make the documentation module useful, we have to register a utility, so why
not the documentation module itself?

  >>> from zope.app.apidoc.interfaces import IDocumentationModule
  >>> from zope import component as ztapi
  >>> ztapi.provideUtility(module, IDocumentationModule, 'Utility')

Now we can get a single utility interface by path:

  >>> module.get('zope.app.apidoc.interfaces.IDocumentationModule')
  <zope.app.apidoc.utilitymodule.utilitymodule.UtilityInterface ...>

and list all available interfaces:

  >>> module.items()
  [...
   ('zope.app.apidoc.interfaces.IDocumentationModule',
    <zope.app.apidoc.utilitymodule.utilitymodule.UtilityInterface ...>),
   ...
   ('zope.security.interfaces.IPermission',
    <zope.app.apidoc.utilitymodule.utilitymodule.UtilityInterface ...>),
   ...]


:class:`UtilityInterface`
=========================

Representation of an interface a utility provides.

First we create a utility interface documentation instance:

  >>> from zope.app.apidoc.utilitymodule.utilitymodule import UtilityInterface
  >>> ut_iface = UtilityInterface(
  ...     module,
  ...     'zope.app.apidoc.interfaces.IDocumentationModule',
  ...     IDocumentationModule)

Now we can get the utility:

  >>> ut_iface.get('Utility').component
  <zope.app.apidoc.utilitymodule.utilitymodule.UtilityModule object at ...>

Unnamed utilities are special, since they can be looked up in different ways:

  >>> ztapi.provideUtility(module, IDocumentationModule, '')

  >>> ut_iface.get('').component
  <zope.app.apidoc.utilitymodule.utilitymodule.UtilityModule object at ...>

  >>> from zope.app.apidoc.utilitymodule.utilitymodule import NONAME
  >>> ut_iface.get(NONAME).component
  <zope.app.apidoc.utilitymodule.utilitymodule.UtilityModule object at ...>

If you try to get a non-existent utility, ``None`` is returned:

  >>> ut_iface.get('foo') is None
  True

You can get a list of available utilities as well, of course:

  >>> ut_iface.items()
  [...
   ('VXRpbGl0eQ==', <...apidoc.utilitymodule.utilitymodule.Utility ...>),
   ('X19ub25hbWVfXw==', <...apidoc.utilitymodule.utilitymodule.Utility ...>)]

Bu what are those strange names? Since utility names can be any string, it is
hard to deal with them in a URL. Thus the system will advertise and use the
names in their ``BASE64`` encoded form. However, because it is easier in the
Python API to use the real utility names, utilities can be looked up in their
original form as well.


Encoding and Decoding Names
===========================

The utility names are en- and decoded using two helper methods:

  >>> from zope.app.apidoc.utilitymodule.utilitymodule import encodeName
  >>> from zope.app.apidoc.utilitymodule.utilitymodule import decodeName

Round trips of :func:`encoding <encodeName>` and :func:`decoding
<decodeName>` should be possible:

  >>> encoded = encodeName('Some Utility')
  >>> encoded
  'U29tZSBVdGlsaXR5'

  >>> decodeName(encoded)
  'Some Utility'

If a string is not encoded, the decoding process will simply return the
original string:

  >>> decodeName('Some Utility')
  'Some Utility'
