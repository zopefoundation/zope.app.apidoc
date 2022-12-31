==========
 Overview
==========

.. currentmodule:: zope.app.apidoc.apidoc

This Zope 3 package provides fully dynamic API documentation of Zope 3 and
registered add-on components. The package is very extensible and can be easily
extended by implementing new modules.

Besides being an application, the API doctool also provides several public
APIs to extract information from various objects used by Zope 3.

 * utilities -- Miscellaneous classes and functions that aid all documentation
   modules. They are broadly usable.

 * interface -- This module contains functions to inspect interfaces and
   schemas.

 * component -- This modules provides utility functions to lookup components
   given an interface.

 * presentation -- Presentation components are generally more complex than
   others, so a separate utilities module is provided to inspect views.

 * classregistry -- Here a simple dictionary-based registry for all known
   classes is provided. It allows us to search in classes.


Using the API Dcoumentation
===========================

The :class:`APIDocumentation` class provides
access to all available documentation modules. Documentation modules
are utilities providing :class:`~zope.app.apidoc.interfaces.IDocumentationModule`:


  >>> from zope import component as ztapi
  >>> from zope.app.apidoc.interfaces import IDocumentationModule
  >>> from zope.app.apidoc.ifacemodule.ifacemodule import InterfaceModule
  >>> from zope.app.apidoc.zcmlmodule import ZCMLModule

  >>> ztapi.provideUtility(InterfaceModule(), IDocumentationModule,
  ...                      'Interface')
  >>> ztapi.provideUtility(ZCMLModule(), IDocumentationModule, 'ZCML')

Now we can instantiate the class (which is usually done when traversing
'++apidoc++') and get a list of available modules:

  >>> from zope.app.apidoc.apidoc import APIDocumentation
  >>> doc = APIDocumentation(None, '++apidoc++')

  >>> modules = sorted(doc.keys())
  >>> modules
  ['Interface', 'ZCML']

  >>> doc['ZCML']
  <zope.app.apidoc.zcmlmodule.ZCMLModule 'ZCML' at ...>


Developing a Module
===================

1. Implement a class that realizes the :class:`~zope.app.apidoc.interfaces.IDocumentationModule`
   interface.

2. Register this class as a utility using something like this::

     <utility
         provides="zope.app.apidoc.interfaces.IDocumentationModule"
         factory=".examplemodule.ExampleModule"
         name="Example" />

3. Take care of security by allowing at least :class:`~zope.app.apidoc.interfaces.IDocumentationModule`::

     <class class=".ExampleModule">
       <allow interface="zope.app.apidoc.interfaces.IDocumentationModule" />
     </class>

4. Provide a browser view called ``menu.html``.

5. Provide another view, usually ``index.html``, that can show the
   details for the various menu items.

Note:  There are several modules that come with the product. Just look
in them for some guidance.


New Static APIDOC-Version
=========================

An alternative APIDOC-Version is available through ``++apidoc++/static.html``
Find and Tree are implemented in Javascript, so it should be possible to do a
"wget" - Offline-Version of APIDOC.

In fact, this package comes with a somewhat smarter version of "wget"
that can load a Zope configuration and export the documentation. For
more information, see :doc:`static`.
