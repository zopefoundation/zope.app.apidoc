Zope 3 API Documentation
========================

This Zope 3 product provides a fully dynamic API documentation of Zope 3 and
registered add-on components. The product is very extensible and can be easily
extended by implementing new modules.


Developing a Module
-------------------

1. Implement a class that realizes the `IDocumentationModule`
   interface.

2. Register this class as a utility using something like this::

     <utility
         provides="zope.app.apidoc.interfaces.IDocumentationModule"
         factory=".examplemodule.ExampleModule"
         name="Example" />

3. Take care of security by allowing at least `IDocumentationModule`::

     <class class=".ExampleModule">
       <allow interface="zope.app.apidoc.interfaces.IDocumentationModule" />
     </class>

4. Provide a browser view called ``menu.html``.

5. Provide another view, usually ``index.html``, that can show the
   details for the various menu items.

Note:  There are several modules that come with the product. Just look
in them for some guidance.
