===================================
 Presentation Inspection Utilities
===================================

.. currentmodule:: zope.app.apidoc.presentation

The ``presentation`` module provides some nice utilities to inspect presentation
registrations.

  >>> from zope.app.apidoc import presentation


:func:`getViewFactoryData`
==========================

This function tries really hard to determine the correct information about a
view factory. For example, when you create a page, a new type is dynamically
generated upon registration. Let's look at a couple examples.

First, let's inspect a case where a simple browser page was configured without
a special view class. In these cases the factory is a :class:`~.SimpleViewClass`:

  >>> from zope.browserpage.simpleviewclass import SimpleViewClass
  >>> view = SimpleViewClass('browser/index.pt')
  >>> info = presentation.getViewFactoryData(view)

Before we can check the result, we have to make sure that all Windows paths
are converted to Unix-like paths. We also clip off instance-specific parts of
the template path:

  >>> info['template'] = info['template'].replace('\\', '/')[-32:]
  >>> from pprint import pprint
  >>> pprint(info)
  {'path': 'zope.browserpage.simpleviewclass.simple',
   'referencable': True,
   'resource': None,
   'template': 'zope/app/apidoc/browser/index.pt',
   'template_obj': <BoundPageTemplateFile of None>,
   'url': 'zope/browserpage/simpleviewclass/simple'}

So in the result above we see what the function returns. It is a dictionary
(converted to a list for test purposes) that contains the Python path of the
view class, a flag that specifies whether the factory can be referenced and
thus be viewed by the class browser, the (page) template used for the view and
the URL under which the factory will be found in the class browser. Some
views, like icons, also use resources to provide their data. In these cases
the name of the resource will be provided. Of course, not in all cases all
values will be available. Empty values are marked with ``None``.

Believe it or not, in some cases the factory is just a simple type. In these
cases we cannot retrieve any useful information:

  >>> info = presentation.getViewFactoryData(3)
  >>> pprint(info)
  {'path': '__builtin__.int',
   'referencable': False,
   'resource': None,
   'template': None,
   'url': None}

In some cases factories are callable class instances, where we cannot directly
have a referencable name, so we lookup the class and use its name:

  >>> class Factory(object):
  ...     pass

  >>> info = presentation.getViewFactoryData(Factory())
  >>> pprint(info)
  {'path': 'zope.app.apidoc.doctest.Factory',
   'referencable': True,
   'resource': None,
   'template': None,
   'url': 'zope/app/apidoc/doctest/Factory'}

One of the more common cases, however, is that the factory is a class or
type. In this case we can just retrieve the reference directly:

  >>> info = presentation.getViewFactoryData(Factory)
  >>> pprint(info)
  {'path': 'zope.app.apidoc.doctest.Factory',
   'referencable': True,
   'resource': None,
   'template': None,
   'url': 'zope/app/apidoc/doctest/Factory'}

When factories are created by a directive, they can also be functions. In
those cases we just simply return the function path:

  >>> def factory():
  ...     pass
  >>> factory.__module__ = 'zope.app.apidoc.doctest' # The testing framework does not set the __module__ correctly

  >>> info = presentation.getViewFactoryData(factory)
  >>> pprint(info)
  {'path': 'zope.app.apidoc.doctest.factory',
   'referencable': True,
   'resource': None,
   'template': None,
   'url': 'zope/app/apidoc/doctest/factory'}

However, the function is rather unhelpful, since it will be the same for all
views that use that code path. For this reason the function keeps track of the
original factory component in a function attribute called ``factory``:

  >>> factory.factory = Factory

  >>> info = presentation.getViewFactoryData(factory)
  >>> pprint(info)
  {'path': 'zope.app.apidoc.doctest.Factory',
   'referencable': True,
   'resource': None,
   'template': None,
   'url': 'zope/app/apidoc/doctest/Factory'}

Let's now have a look at some extremly specific cases. If a view is registered
using the ``zope:view`` directive and a permission is specified, a
``ProxyView`` class instance is created that references its original factory:

  >>> class ProxyView(object):
  ...
  ...     def __init__(self, factory):
  ...         self.factory = factory
  >>> proxyView = ProxyView(Factory)

  >>> info = presentation.getViewFactoryData(proxyView)
  >>> pprint(info)
  {'path': 'zope.app.apidoc.doctest.Factory',
   'referencable': True,
   'resource': None,
   'template': None,
   'url': 'zope/app/apidoc/doctest/Factory'}

Another use case is when a new type is created by the ``browser:page`` or
``browser:view`` directive. In those cases the true/original factory is really
the first base class. Those cases are detected by inspecting the
``__module__`` string of the type:

  >>> new_class = type(Factory.__name__, (Factory,), {})
  >>> new_class.__module__ = 'zope.app.publisher.browser.viewmeta'

  >>> info = presentation.getViewFactoryData(new_class)
  >>> pprint(info)
  {'path': 'zope.app.apidoc.doctest.Factory',
   'referencable': True,
   'resource': None,
   'template': None,
   'url': 'zope/app/apidoc/doctest/Factory'}

The same sort of thing happens for XML-RPC views, except that those are
wrapped twice:

  >>> new_class = type(Factory.__name__, (Factory,), {})
  >>> new_class.__module__ = 'zope.app.publisher.xmlrpc.metaconfigure'

  >>> new_class2 = type(Factory.__name__, (new_class,), {})
  >>> new_class2.__module__ = 'zope.app.publisher.xmlrpc.metaconfigure'

  >>> info = presentation.getViewFactoryData(new_class2)
  >>> pprint(info)
  {'path': 'zope.app.apidoc.doctest.Factory',
   'referencable': True,
   'resource': None,
   'template': None,
   'url': 'zope/app/apidoc/doctest/Factory'}

Finally, it sometimes happens that a factory is wrapped and the wrapper is
wrapped in return:

  >>> def wrapper1(*args):
  ...     return Factory(*args)

  >>> def wrapper2(*args):
  ...     return wrapper1(*args)

Initially, the documentation is not very helpful:

  >>> info = presentation.getViewFactoryData(wrapper2)
  >>> pprint(info)
  {'path': 'zope.app.apidoc.doctest.wrapper2',
   'referencable': True,
   'resource': None,
   'template': None,
   'url': 'zope/app/apidoc/doctest/wrapper2'}

However, if those wrappers play nicely, they provide a factory attribute each
step of the way ...

  >>> wrapper1.factory = Factory
  >>> wrapper2.factory = wrapper1

and the result is finally our original factory:

  >>> info = presentation.getViewFactoryData(wrapper2)
  >>> pprint(info)
  {'path': 'zope.app.apidoc.doctest.Factory',
   'referencable': True,
   'resource': None,
   'template': None,
   'url': 'zope/app/apidoc/doctest/Factory'}


:func:`getPresentationType`
===========================

In Zope 3, presentation types (i.e. browser, ftp, ...) are defined through
their special request interface, such as :class:`~.IBrowserRequest` or
:class:`~.IFTPRequest`. To complicate matters further, layer interfaces are used in
browser presentations to allow skinning. Layers extend any request type, but
most commonly ``IBrowserRequest``. This function inspects the request interface
of any presentation multi-adapter and determines its type, which is returned
in form of an interface.

  >>> from zope.app.apidoc.presentation import getPresentationType
  >>> from zope.publisher.interfaces.http import IHTTPRequest
  >>> from zope.publisher.interfaces.browser import IBrowserRequest

  >>> class ILayer1(IBrowserRequest):
  ...     pass

  >>> presentation.getPresentationType(ILayer1)
  <InterfaceClass zope.publisher.interfaces.browser.IBrowserRequest>

  >>> class ILayer2(IHTTPRequest):
  ...     pass

  >>> presentation.getPresentationType(ILayer2)
  <InterfaceClass zope.publisher.interfaces.http.IHTTPRequest>

If the function cannot determine the presentation type, the interface itself
is returned:

  >>> from zope.interface import Interface
  >>> class ILayer3(Interface):
  ...     pass

  >>> presentation.getPresentationType(ILayer3)
  <InterfaceClass zope.app.apidoc.doctest.ILayer3>

Note that more specific presentation types are considered first. For
example, :class:`zope.publisher.interfaces.browser.IBrowserRequest`
extends :class:`zope.publisher.interfaces.http.IHTTPRequest`, but it
will always determine the presentation type to be an
:class:`~zope.publisher.interfaces.browser.IBrowserRequest`.


:func:`getViews`
================

This function retrieves all available view registrations for a given
interface and presentation type. The default argument for the
presentation type is :class:`zope.publisher.interfaces.IRequest`,
which will effectively return all views for the specified interface.

To see how this works, we first have to register some views:

  >>> class IFoo(Interface):
  ...     pass

  >>> from zope import component as ztapi
  >>> ztapi.provideAdapter(adapts=(IFoo, IHTTPRequest), provides=Interface, factory=None, name='foo')
  >>> ztapi.provideAdapter(adapts=(Interface, IHTTPRequest), provides=Interface, factory=None,
  ...                      name='bar')
  >>> ztapi.provideAdapter(adapts=(IFoo, IBrowserRequest), provides=Interface, factory=None,
  ...                      name='blah')

Now let's see what we've got. If we do not specify a type, all registrations
should be returned:

  >>> regs = list(presentation.getViews(IFoo))
  >>> regs.sort()
  >>> regs
  [AdapterRegistration(<BaseGlobalComponents base>,
                       [IFoo, IBrowserRequest], Interface, 'blah', None, u''),
   AdapterRegistration(<BaseGlobalComponents base>,
                       [IFoo, IHTTPRequest], Interface, 'foo', None, u''),
   AdapterRegistration(<BaseGlobalComponents base>,
                       [Interface, IHTTPRequest], Interface, 'bar', None, u'')]

  >>> regs = list(presentation.getViews(Interface, IHTTPRequest))
  >>> regs.sort()
  >>> regs
  [AdapterRegistration(<BaseGlobalComponents base>,
                       [Interface, IHTTPRequest], Interface, 'bar', None, u'')]


:func:`filterViewRegistrations`
===============================

Oftentimes the amount of views that are being returned for a particular
interface are too much to show at once. It is then good to split the view into
categories. The ``filterViewRegistrations()`` function allows you to filter the
views on how specific they are to the interface. Here are the three levels you
can select from:

  * SPECIFC_INTERFACE_LEVEL -- Only return registrations that require the
                               specified interface directly.

  * EXTENDED_INTERFACE_LEVEL -- Only return registrations that require an
                                interface that the specified interface extends.

  * GENERIC_INTERFACE_LEVEL -- Only return registrations that explicitely
                               require the ``Interface`` interface.

So, let's see how this is done. We first need to create a couple of interfaces
and register some views:

  >>> class IContent(Interface):
  ...     pass
  >>> class IFile(IContent):
  ...     pass

  Clear out the registries first, so we know what we have.
  >>> from zope.testing.cleanup import cleanUp
  >>> cleanUp()

  >>> ztapi.provideAdapter(adapts=(IContent, IHTTPRequest), provides=Interface,
  ...                      factory=None, name='view.html')
  >>> ztapi.provideAdapter(adapts=(IContent, IHTTPRequest), provides=Interface,
  ...                      factory=None, name='edit.html')
  >>> ztapi.provideAdapter(adapts=(IFile, IHTTPRequest), provides=Interface,
  ...                      factory=None, name='view.html')
  >>> ztapi.provideAdapter(adapts=(Interface, IHTTPRequest), provides=Interface,
  ...                      factory=None, name='view.html')

Now we get all the registrations:

  >>> regs = list(presentation.getViews(IFile, IHTTPRequest))

Let's now filter those registrations:

  >>> result = list(presentation.filterViewRegistrations(
  ...     regs, IFile, level=presentation.SPECIFIC_INTERFACE_LEVEL))
  >>> result.sort()
  >>> result
  [AdapterRegistration(<BaseGlobalComponents base>,
                     [IFile, IHTTPRequest], Interface, 'view.html', None, u'')]

  >>> result = list(presentation.filterViewRegistrations(
  ...     regs, IFile, level=presentation.EXTENDED_INTERFACE_LEVEL))
  >>> result.sort()
  >>> result
  [AdapterRegistration(<BaseGlobalComponents base>,
                  [IContent, IHTTPRequest], Interface, 'edit.html', None, u''),
   AdapterRegistration(<BaseGlobalComponents base>,
                  [IContent, IHTTPRequest], Interface, 'view.html', None, u'')]

  >>> result = list(presentation.filterViewRegistrations(
  ...     regs, IFile, level=presentation.GENERIC_INTERFACE_LEVEL))
  >>> result.sort()
  >>> result
  [AdapterRegistration(<BaseGlobalComponents base>,
                 [Interface, IHTTPRequest], Interface, 'view.html', None, u'')]

You can also specify multiple levels at once using the Boolean OR operator,
since all three levels are mutually exclusive.

  >>> result = list(presentation.filterViewRegistrations(
  ...     regs, IFile, level=presentation.SPECIFIC_INTERFACE_LEVEL |
  ...                        presentation.EXTENDED_INTERFACE_LEVEL))
  >>> result.sort()
  >>> result
  [AdapterRegistration(<BaseGlobalComponents base>,
                  [IContent, IHTTPRequest], Interface, 'edit.html', None, u''),
   AdapterRegistration(<BaseGlobalComponents base>,
                  [IContent, IHTTPRequest], Interface, 'view.html', None, u''),
   AdapterRegistration(<BaseGlobalComponents base>,
                  [IFile, IHTTPRequest], Interface, 'view.html', None, u'')]

  >>> result = list(presentation.filterViewRegistrations(
  ...     regs, IFile, level=presentation.SPECIFIC_INTERFACE_LEVEL |
  ...                        presentation.GENERIC_INTERFACE_LEVEL))
  >>> result.sort()
  >>> result
  [AdapterRegistration(<BaseGlobalComponents base>,
                [IFile, IHTTPRequest], Interface, 'view.html', None, u''),
   AdapterRegistration(<BaseGlobalComponents base>,
                [Interface, IHTTPRequest], Interface, 'view.html', None, u'')]


:func:`getViewInfoDictionary`
=============================

Now that we have all these utilities to select the registrations, we need to
prepare the them for output. For page templates the best data structures are
dictionaries and tuples/lists. This utility will generate an informational
dictionary for the specified registration.

Let's first create a registration:

  >>> from zope.interface.registry import AdapterRegistration
  >>> reg = AdapterRegistration(None, (IFile, Interface, IHTTPRequest),
  ...                           Interface, 'view.html', Factory, 'reg info')

  >>> pprint(presentation.getViewInfoDictionary(reg), width=50)
  {'doc': 'reg info',
   'factory': {'path': 'zope.app.apidoc.doctest.Factory',
               'referencable': True,
               'resource': None,
               'template': None,
               'url': 'zope/app/apidoc/doctest/Factory'},
   'name': u'view.html',
   'provided': {'module': 'zope.interface',
                'name': 'Interface'},
   'read_perm': None,
   'required': [{'module': 'zope.app.apidoc.doctest',
                 'name': 'IFile'},
                {'module': 'zope.interface',
                 'name': 'Interface'},
                {'module': 'zope.publisher.interfaces.http',
                 'name': 'IHTTPRequest'}],
   'type': 'zope.publisher.interfaces.http.IHTTPRequest',
   'write_perm': None,
   'zcml': None}
