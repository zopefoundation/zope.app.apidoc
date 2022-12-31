================================
 Component Inspection Utilities
================================

.. currentmodule:: zope.app.apidoc.component

Once you have an interface, you really want to discover on how this interface
interacts with other components in Zope 3. The functions in

  >>> from zope.app.apidoc import component

provide you with utilities to make those discoveries. The functions are
explained in detail in this document. Before we start though, we have to have
some interfaces to work with:

  >>> from zope.interface import Interface
  >>> class IFoo(Interface):
  ...     pass

  >>> class IBar(Interface):
  ...     pass

  >>> class IFooBar(IFoo, IBar):
  ...     pass

  >>> class IResult(Interface):
  ...     pass

  >>> class ISpecialResult(IResult):
  ...     pass


:func:`getRequiredAdapters`
===========================

This function returns adapter registrations for adapters that require the
specified interface. So let's create some adapter registrations:

  >>> from zope.publisher.interfaces import IRequest
  >>> from zope import component as ztapi
  >>> ztapi.provideAdapter(adapts=(IFoo,), provides=IResult, factory=None)
  >>> ztapi.provideAdapter(adapts=(IFoo, IBar), provides=ISpecialResult, factory=None)
  >>> ztapi.provideAdapter(adapts=(IFoo, IRequest), provides=ISpecialResult, factory=None)
  >>> ztapi.provideHandler(adapts=(IFoo,), factory='stubFactory')

  >>> regs = list(component.getRequiredAdapters(IFoo))
  >>> regs.sort()
  >>> regs
  [AdapterRegistration(<BaseGlobalComponents base>,
                       [IFoo, IBar], ISpecialResult, '', None, ''),
   AdapterRegistration(<BaseGlobalComponents base>,
                       [IFoo], IResult, '', None, ''),
   HandlerRegistration(<BaseGlobalComponents base>,
                       [IFoo], '', 'stubFactory', '')]

Note how the adapter requiring an
:class:`zope.publisher.interfaces.IRequest` at the end of the required
interfaces is neglected. This is because it is recognized as a view
and views are not returned by default. But you can simply turn this
flag on:

  >>> regs = list(component.getRequiredAdapters(IFoo, withViews=True))
  >>> regs.sort()
  >>> regs
  [AdapterRegistration(<BaseGlobalComponents base>,
                       [IFoo, IBar], ISpecialResult, '', None, ''),
   AdapterRegistration(<BaseGlobalComponents base>,
                       [IFoo, IRequest], ISpecialResult, '', None, ''),
   AdapterRegistration(<BaseGlobalComponents base>,
                       [IFoo], IResult, '', None, ''),
   HandlerRegistration(<BaseGlobalComponents base>,
                       [IFoo], '', 'stubFactory', '')]

The function will also pick up registrations that have required interfaces the
specified interface extends:

  >>> regs = list(component.getRequiredAdapters(IFoo))
  >>> regs.sort()
  >>> regs
  [AdapterRegistration(<BaseGlobalComponents base>,
                       [IFoo, IBar], ISpecialResult, '', None, ''),
   AdapterRegistration(<BaseGlobalComponents base>,
                       [IFoo], IResult, '', None, ''),
   HandlerRegistration(<BaseGlobalComponents base>,
                       [IFoo], '', 'stubFactory', '')]

And all of the required interfaces are considered, of course:

  >>> regs = list(component.getRequiredAdapters(IBar))
  >>> regs.sort()
  >>> regs
  [AdapterRegistration(<BaseGlobalComponents base>,
                       [IFoo, IBar], ISpecialResult, '', None, '')]


:func:`getProvidedAdapters`
===========================

Of course, we are also interested in the adapters that provide a certain
interface. This function returns those adapter registrations, again ignoring
views by default.

  >>> regs = list(component.getProvidedAdapters(ISpecialResult))
  >>> regs.sort()
  >>> regs
  [AdapterRegistration(<BaseGlobalComponents base>,
                       [IFoo, IBar], ISpecialResult, '', None, '')]

And by specifying the ``withView`` flag, we get views as well:

  >>> regs = list(component.getProvidedAdapters(ISpecialResult, withViews=True))
  >>> regs.sort()
  >>> regs
  [AdapterRegistration(<BaseGlobalComponents base>,
                       [IFoo, IBar], ISpecialResult, '', None, ''),
   AdapterRegistration(<BaseGlobalComponents base>,
                       [IFoo, IRequest], ISpecialResult, '', None, '')]

We can of course also ask for adapters specifying ``IResult``:

  >>> regs = list(component.getProvidedAdapters(IResult, withViews=True))
  >>> regs.sort()
  >>> regs
  [AdapterRegistration(<BaseGlobalComponents base>,
                       [IFoo, IBar], ISpecialResult, '', None, ''),
   AdapterRegistration(<BaseGlobalComponents base>,
                       [IFoo, IRequest], ISpecialResult, '', None, ''),
   AdapterRegistration(<BaseGlobalComponents base>,
                       [IFoo], IResult, '', None, '')]


:func:`getClasses`
==================

This package comes with a little tool called the class registry
(see :doc:`classregistry`). It provides a dictionary of all classes in the
visible packages. This function utilizes the registry to retrieve all classes
that implement the specified interface.

Let's start by creating and registering some classes:

  >>> from zope.interface import implementer
  >>> from zope.app.apidoc.classregistry import classRegistry

  >>> @implementer(IFoo)
  ... class MyFoo(object):
  ...    pass
  >>> classRegistry['MyFoo'] = MyFoo

  >>> @implementer(IBar)
  ... class MyBar(object):
  ...    pass
  >>> classRegistry['MyBar'] = MyBar

  >>> @implementer(IFooBar)
  ... class MyFooBar(object):
  ...    pass
  >>> classRegistry['MyFooBar'] = MyFooBar

Let's now see whether what results we get:

  >>> classes = component.getClasses(IFooBar)
  >>> classes.sort()
  >>> classes
  [('MyFooBar', <class 'zope.app.apidoc.doctest.MyFooBar'>)]

  >>> classes = component.getClasses(IFoo)
  >>> classes.sort()
  >>> classes
  [('MyFoo', <class 'zope.app.apidoc.doctest.MyFoo'>),
   ('MyFooBar', <class 'zope.app.apidoc.doctest.MyFooBar'>)]


:func:`getFactories`
====================

Return the factory registrations of the factories that will return objects
providing this interface.

Again, the first step is to create some factories:

  >>> from zope.component.factory import Factory
  >>> from zope.component.interfaces import IFactory
  >>> ztapi.provideUtility(Factory(MyFoo), IFactory, 'MyFoo')
  >>> ztapi.provideUtility(Factory(MyBar), IFactory, 'MyBar')
  >>> ztapi.provideUtility(
  ...     Factory(MyFooBar, 'MyFooBar', 'My Foo Bar'), IFactory, 'MyFooBar')

Let's see whether we will be able to get them:

  >>> regs = list(component.getFactories(IFooBar))
  >>> regs.sort()
  >>> regs
  [UtilityRegistration(<BaseGlobalComponents base>,
      IFactory, 'MyFooBar',
      <Factory for <class 'zope.app.apidoc.doctest.MyFooBar'>>, None, '')]

  >>> regs = list(component.getFactories(IFoo))
  >>> regs.sort()
  >>> regs
  [UtilityRegistration(<BaseGlobalComponents base>, IFactory, 'MyFoo',
               <Factory for <class 'zope.app.apidoc.doctest.MyFoo'>>, None, ''),
   UtilityRegistration(<BaseGlobalComponents base>, IFactory, 'MyFooBar',
            <Factory for <class 'zope.app.apidoc.doctest.MyFooBar'>>, None, '')]


:func:`getUtilities`
====================

Return all utility registrations for utilities that provide the specified
interface.

As usual, we have to register some utilities first:

  >>> ztapi.provideUtility(MyFoo(), IFoo)
  >>> ztapi.provideUtility(MyBar(), IBar)
  >>> ztapi.provideUtility(MyFooBar(), IFooBar)

Now let's have a look what we have:

  >>> regs = list(component.getUtilities(IFooBar))
  >>> regs.sort()
  >>> regs
  [UtilityRegistration(<BaseGlobalComponents base>, IFooBar, '',
                       <zope.app.apidoc.doctest.MyFooBar object at ...>, None, '')]

  >>> regs = list(component.getUtilities(IFoo))
  >>> regs.sort()
  >>> regs
  [UtilityRegistration(<BaseGlobalComponents base>, IFoo, '',
                       <zope.app.apidoc.doctest.MyFoo object at ...>, None, ''),
   UtilityRegistration(<BaseGlobalComponents base>, IFooBar, '',
                       <zope.app.apidoc.doctest.MyFooBar object at ...>, None, '')]


:func:`getRealFactory`
======================

During registration, factories are commonly masked by wrapper functions. Also,
factories are sometimes also ``IFactory`` instances, which are not referencable,
so that we would like to return the class. If the wrapper objects/functions
play nice, then they provide a ``factory`` attribute that points to the next
wrapper or the original factory.

The task of this function is to remove all the factory wrappers and make sure
that the returned factory is referencable.

  >>> class Factory(object):
  ...     pass

  >>> def wrapper1(*args):
  ...     return Factory(*args)
  >>> wrapper1.factory = Factory

  >>> def wrapper2(*args):
  ...     return wrapper1(*args)
  >>> wrapper2.factory = wrapper1

So whether we pass in ``Factory``,

  >>> component.getRealFactory(Factory)
  <class 'zope.app.apidoc.doctest.Factory'>

``wrapper1``,

  >>> component.getRealFactory(wrapper1)
  <class 'zope.app.apidoc.doctest.Factory'>

or ``wrapper2``,

  >>> component.getRealFactory(wrapper2)
  <class 'zope.app.apidoc.doctest.Factory'>

the answer should always be the ``Factory`` class. Next we are going to pass in
an instance, and again we should get our class aas a result:

  >>> factory = Factory()
  >>> component.getRealFactory(factory)
  <class 'zope.app.apidoc.doctest.Factory'>

Even, if the factory instance is wrapped, we should get the factory class:

  >>> def wrapper3(*args):
  ...     return factory(*args)
  >>> wrapper3.factory = factory

  >>> component.getRealFactory(wrapper3)
  <class 'zope.app.apidoc.doctest.Factory'>


:func:`getInterfaceInfoDictionary`
==================================

This function returns a small info dictionary for an interface. It only
reports the module and the name. This is useful for cases when we only want to
list interfaces in the context of other components, like adapters and
utilities.

  >>> from pprint import pprint
  >>> pprint(component.getInterfaceInfoDictionary(IFoo), width=1)
  {'module': 'zope.app.apidoc.doctest', 'name': 'IFoo'}

The functions using this function use it with little care and can also
sometimes pass in ``None``. In these cases we want to return ``None``:

  >>> component.getInterfaceInfoDictionary(None) is None
  True

It's also possible for this function to be passed a
zope.interface.declarations.Implements instance.  For instance, this function
is sometimes used to analyze the required elements of an adapter registration:
if an adapter or subscriber is registered against a class, then the required
element will be an Implements instance.  In this case, we currently believe
that we want to return the module and name of the object that the Implements
object references.  This may change.

  >>> from zope.interface import implementedBy
  >>> pprint(component.getInterfaceInfoDictionary(implementedBy(MyFoo)), width=1)
  {'module': 'zope.app.apidoc.doctest', 'name': 'MyFoo'}


:func:`getTypeInfoDictionary`
=============================

This function returns the info dictionary of a type.

  >>> pprint(component.getTypeInfoDictionary(tuple), width=1)
  {'module': 'builtins',
   'name': 'tuple',
   'url': 'builtins/tuple'}


:func:`getSpecificationInfoDictionary`
======================================

Thsi function returns an info dictionary for the given specification. A
specification can either be an interface or class. If it is an interface, it
simply returns the interface dictionary:

  >>> pprint(component.getSpecificationInfoDictionary(IFoo))
  {'isInterface': True,
   'isType': False,
   'module': 'zope.app.apidoc.doctest',
   'name': 'IFoo'}

In addition to the usual interface infos, there are two flags indicating
whether the specification was an interface or type. In our case it is an
interface.

Let's now look at the behavior when passing a type:

  >>> import zope.interface
  >>> tupleSpec = zope.interface.implementedBy(tuple)

  >>> pprint(component.getSpecificationInfoDictionary(tupleSpec))
  {'isInterface': False,
   'isType': True,
   'module': 'builtins',
   'name': 'tuple',
   'url': 'builtins/tuple'}

For the type, we simply reuse the type info dictionary function.


:func:`getAdapterInfoDictionary`
================================

This function returns a page-template-friendly dictionary representing the
data of an adapter registration in an output-friendly format.

Let's first create an adapter registration:

  >>> @implementer(IResult)
  ... class MyResult(object):
  ...    pass

  >>> from zope.interface.registry import AdapterRegistration
  >>> reg = AdapterRegistration(None, (IFoo, IBar), IResult, 'FooToResult',
  ...                            MyResult, 'doc info')

And now get the info dictionary:

  >>> pprint(component.getAdapterInfoDictionary(reg), width=50)
  {'doc': 'doc info',
   'factory': 'zope.app.apidoc.doctest.MyResult',
   'factory_url': 'zope/app/apidoc/doctest/MyResult',
   'name': 'FooToResult',
   'provided': {'module': 'zope.app.apidoc.doctest',
                'name': 'IResult'},
   'required': [{'isInterface': True,
                 'isType': False,
                 'module': 'zope.app.apidoc.doctest',
                 'name': 'IFoo'},
                {'isInterface': True,
                 'isType': False,
                 'module': 'zope.app.apidoc.doctest',
                 'name': 'IBar'}],
   'zcml': None}

If the factory's path cannot be referenced, for example if a type has been
created using the ``type()`` builtin function, then the URL of the factory
will be ``None``:

  >>> MyResultType = type('MyResult2', (object,), {})
  >>> from zope.interface import classImplements
  >>> classImplements(MyResultType, IResult)

  >>> reg = AdapterRegistration(None, (IFoo, IBar), IResult, 'FooToResult',
  ...                            MyResultType, 'doc info')
  >>> pprint(component.getAdapterInfoDictionary(reg), width=50)
  {'doc': 'doc info',
   'factory': 'zope.app.apidoc.doctest.MyResult2',
   'factory_url': None,
   'name': 'FooToResult',
   'provided': {'module': 'zope.app.apidoc.doctest',
                'name': 'IResult'},
   'required': [{'isInterface': True,
                 'isType': False,
                 'module': 'zope.app.apidoc.doctest',
                 'name': 'IFoo'},
                {'isInterface': True,
                 'isType': False,
                 'module': 'zope.app.apidoc.doctest',
                 'name': 'IBar'}],
   'zcml': None}

This function can also handle subscription registrations, which are pretty
much like adapter registrations, except that they do not have a name. So let's
see how the function handles subscriptions:

  >>> from zope.interface.registry import HandlerRegistration
  >>> reg = HandlerRegistration(None, (IFoo, IBar), '', MyResult, 'doc info')

  >>> pprint(component.getAdapterInfoDictionary(reg))
  {'doc': 'doc info',
   'factory': 'zope.app.apidoc.doctest.MyResult',
   'factory_url': 'zope/app/apidoc/doctest/MyResult',
   'name': '',
   'provided': None,
   'required': [{'isInterface': True,
                 'isType': False,
                 'module': 'zope.app.apidoc.doctest',
                 'name': 'IFoo'},
                {'isInterface': True,
                 'isType': False,
                 'module': 'zope.app.apidoc.doctest',
                 'name': 'IBar'}],
   'zcml': None}


:func:`getFactoryInfoDictionary`
================================

This function returns a page-template-friendly dictionary representing the
data of a factory (utility) registration in an output-friendly format.

Luckily we have already registered some factories, so we just reuse their
registrations:

  >>> pprint(component.getFactoryInfoDictionary(
  ...     next(component.getFactories(IFooBar))))
  {'description': '<p>My Foo Bar</p>\n',
   'name': 'MyFooBar',
   'title': 'MyFooBar',
   'url': 'zope/app/apidoc/doctest/MyFooBar'}

If the factory's path cannot be referenced, for example if a type has been
created using the ``type()`` builtin function, then the URL of the factory
will be ``None``:

  >>> class IMine(Interface):
  ...     pass

  >>> class FactoryBase(object):
  ...     def getInterfaces(self): return [IMine]

  >>> MyFactoryType = type('MyFactory', (FactoryBase,), {})
  >>> from zope.interface import classImplements
  >>> classImplements(MyFactoryType, IFactory)
  >>> ztapi.provideUtility(MyFactoryType(), IFactory, 'MyFactory')

  >>> pprint(component.getFactoryInfoDictionary(
  ...     next(component.getFactories(IMine))), width=50)
  {'description': '',
   'name': 'MyFactory',
   'title': '',
   'url': None}


:func:`getUtilityInfoDictionary`
================================

This function returns a page-template-friendly dictionary representing the
data of a utility registration in an output-friendly format.

Luckily we have already registered some utilities, so we just reuse their
registrations:

  >>> pprint(component.getUtilityInfoDictionary(
  ...     next(component.getUtilities(IFooBar))))
  {'iface_id': 'zope.app.apidoc.doctest.IFooBar',
   'name': '<i>no name</i>',
   'path': 'zope.app.apidoc.doctest.MyFooBar',
   'url': 'Code/zope/app/apidoc/doctest/MyFooBar',
   'url_name': 'X19ub25hbWVfXw=='}
