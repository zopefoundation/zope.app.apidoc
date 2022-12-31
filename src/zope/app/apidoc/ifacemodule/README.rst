====================================
 The Interface Documentation Module
====================================

.. currentmodule:: zope.app.apidoc.ifacemodule.ifacemodule

This documentation module allows you to inspect all aspects of an
interface and its role within the Zope 3 framework. The :class:`module
<InterfaceModule>` can be instantiated like all other documentation
modules:

  >>> from zope.app.apidoc.ifacemodule.ifacemodule import InterfaceModule
  >>> module = InterfaceModule()

After registering an interface

  >>> from zope.interface import Interface
  >>> class IFoo(Interface):
  ...     pass

  >>> from zope.component.interface import provideInterface
  >>> provideInterface(None, IFoo)
  >>> provideInterface('IFoo', IFoo)

Now let's lookup an interface that is registered.

  >>> module.get('IFoo')
  <InterfaceClass builtins.IFoo>

  >>> module.get(IFoo.__module__ + '.IFoo')
  <InterfaceClass builtins.IFoo>


Now we find an interface that is not in the site manager, but exists.

  >>> module.get('zope.app.apidoc.interfaces.IDocumentationModule')
  <InterfaceClass zope.app.apidoc.interfaces.IDocumentationModule>

Finally, you can list all registered interfaces:

  >>> ifaces = sorted(module.items())
  >>> from pprint import pprint
  >>> pprint(ifaces)
  [...
   ('IFoo', <InterfaceClass builtins.IFoo>),
   ...
   ('builtins.IFoo', <InterfaceClass builtins.IFoo>),
    ...]
