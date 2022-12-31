======================================
 Code Browser Presentation Components
======================================

.. currentmodule:: zope.app.apidoc.codemodule.browser

This document describes the API of the views complementing the various code
browser documentation components. The views can be found in

  >>> from zope.app.apidoc.codemodule import browser

We will also need the code browser documentation module:

  >>> cm = apidoc.get('Code')

The ``zope`` package is already registered and available with the code module.


Module Details
==============

The module details are easily created, since we can just use the traversal
process to get a module documentation object:

  >>> from zope.traversing.api import traverse
  >>> _context = traverse(cm, 'zope/app/apidoc/codemodule/codemodule')
  >>> from zope.publisher.browser import TestRequest
  >>> details = browser.module.ModuleDetails(_context, TestRequest())

:meth:`module.ModuleDetails.getDoc`
-----------------------------------

Get the doc string of the module formatted in STX or ReST.

  >>> print(details.getDoc().strip())
  <p>Code Documentation Module</p>
  <p>This module is able to take a dotted name of any class and display
  documentation for it.</p>

Module data
-----------

Return info objects for all classes in this module.

  >>> from pprint import pprint
  >>> pprint(details.getClasses())
  [{'doc': 'Represent the code browser documentation root',
    'name': 'CodeModule',
    'url': 'http://127.0.0.1/++apidoc++/Code/zope/app/apidoc/codemodule/codemodule/CodeModule'}]

This module doesn't contain anything else.

  >>> pprint(details.getInterfaces())
  []
  >>> pprint(details.getModules())
  []
  >>> pprint(details.getModuleInterfaces())
  []
  >>> pprint(details.getTextFiles())
  []
  >>> pprint(details.getZCMLFiles())
  []
  >>> pprint(details.getFunctions())
  []

:func:`utilities.getBreadCrumbs`
--------------------------------

Create breadcrumbs for the module path.

We cannot reuse the the system's bread crumbs, since they go all the
way up to the root, but we just want to go to the root module.

  >>> from zope.app.apidoc.codemodule.browser import utilities
  >>> bc = utilities.CodeBreadCrumbs()
  >>> bc.context = details.context
  >>> bc.request = details.request
  >>> pprint(bc(), width=1)
  [{'name': '[top]',
    'url': 'http://127.0.0.1/++apidoc++/Code'},
   {'name': 'zope',
    'url': 'http://127.0.0.1/++apidoc++/Code/zope'},
   {'name': 'app',
    'url': 'http://127.0.0.1/++apidoc++/Code/zope/app'},
   {'name': 'apidoc',
    'url': 'http://127.0.0.1/++apidoc++/Code/zope/app/apidoc'},
   {'name': 'codemodule',
    'url': 'http://127.0.0.1/++apidoc++/Code/zope/app/apidoc/codemodule'},
   {'name': 'codemodule',
    'url': 'http://127.0.0.1/++apidoc++/Code/zope/app/apidoc/codemodule/codemodule'}]

Module Details With Interfaces
------------------------------

Let's also look at a module that defines interfaces:

  >>> _context = traverse(cm, 'zope/app/apidoc/interfaces')
  >>> details = browser.module.ModuleDetails(_context, TestRequest())
  >>> pprint(details.getInterfaces())
  [{'doc': 'Zope 3 API Documentation Module',
    'name': 'IDocumentationModule',
    'path': 'zope.app.apidoc.interfaces.IDocumentationModule',
    'url': 'http://127.0.0.1/++apidoc++/Code/zope/app/apidoc/interfaces/IDocumentationModule'}]

Module Details With Implementation
----------------------------------

Let's also look at a module that implements an interface itself:

  >>> _context = traverse(cm, 'zope/lifecycleevent')
  >>> details = browser.module.ModuleDetails(_context, TestRequest())
  >>> pprint(details.getModuleInterfaces())
  [{'name': 'IZopeLifecycleEvent',
    'path': 'zope.lifecycleevent.interfaces.IZopeLifecycleEvent'}]


Class Details
=============

The class details are easily created, since we can just use the traversal
process to get a class documentation object:

  >>> details = browser.class_.ClassDetails()
  >>> details.context = traverse(
  ...     cm, 'zope/app/apidoc/codemodule/codemodule/CodeModule')

  >>> details.request = TestRequest()

Now that we have the details class we can just access the various methods:

:meth:`class_.ClassDetails.getBases`
------------------------------------

Get all bases of this class.

  >>> pprint(details.getBases())
  [{'path': 'zope.app.apidoc.codemodule.module.Module',
    'url': 'http://127.0.0.1/++apidoc++/Code/zope/app/apidoc/codemodule/module/Module'}]

:meth:`class_.ClassDetails.getKnownSubclasses`
----------------------------------------------
Get all known subclasses of this class.

  >>> details.getKnownSubclasses()
  []

:meth:`class_.ClassDetails._listClasses`
----------------------------------------

Prepare a list of classes for presentation.

  >>> import zope.app.apidoc.apidoc
  >>> import zope.app.apidoc.codemodule.codemodule

  >>> pprint(details._listClasses([
  ...       zope.app.apidoc.apidoc.APIDocumentation,
  ...       zope.app.apidoc.codemodule.codemodule.Module]))
  [{'path': 'zope.app.apidoc.apidoc.APIDocumentation',
    'url': 'http://127.0.0.1/++apidoc++/Code/zope/app/apidoc/apidoc/APIDocumentation'},
   {'path': 'zope.app.apidoc.codemodule.module.Module',
    'url': 'http://127.0.0.1/++apidoc++/Code/zope/app/apidoc/codemodule/module/Module'}]

:meth:`class_.ClassDetails.getBaseURL`
--------------------------------------

Return the URL for the API Documentation Tool.

Note that the following output is a bit different than usual, since
we have not setup all path elements.

  >>> details.getBaseURL()
  'http://127.0.0.1/++apidoc++'

:meth:`class_.ClassDetails.getInterfaces`
-----------------------------------------

Get all implemented interfaces (as paths) of this class.

  >>> pprint(details.getInterfaces())
  [{'path': 'zope.app.apidoc.interfaces.IDocumentationModule',
    'url': 'zope.app.apidoc.interfaces.IDocumentationModule'},
   {'path': 'zope.location.interfaces.ILocation',
    'url': 'zope.location.interfaces.ILocation'},
   {'path': 'zope.app.apidoc.codemodule.interfaces.IModuleDocumentation',
    'url': 'zope.app.apidoc.codemodule.interfaces.IModuleDocumentation'},
   {'path': 'zope.container.interfaces.IReadContainer',
    'url': 'zope.container.interfaces.IReadContainer'}]

:meth:`class_.ClassDetails.getConstructor`
------------------------------------------

Get info about the class' __init__ method, which is its constructor.

  >>> pprint(details.getConstructor())
  {'doc': '<p>Initialize object.</p>\n',
   'signature': '()'}

:meth:`class_.ClassDetails.getAttributes`
-----------------------------------------

Get all attributes of this class.

  >>> pprint(details.getAttributes()[1])
  {'interface': {'path': 'zope.app.apidoc.interfaces.IDocumentationModule',
                 'url': 'zope.app.apidoc.interfaces.IDocumentationModule'},
   'name': 'title',
   'read_perm': 'zope.Public',
   'type': 'Message',
   'type_link': 'zope/i18nmessageid/message/Message',
   'value': "'Code Browser'",
   'write_perm': 'n/a'}

:meth:`class_.ClassDetails.getMethods`
--------------------------------------
Get all methods of this class.

  >>> pprint(details.getMethods()[-3:-1])
  [{'doc': '<p>Setup module and class tree.</p>\n',
    'interface': None,
    'name': 'setup',
    'read_perm': 'n/a',
    'signature': '()',
    'write_perm': 'n/a'},
   {'doc': '',
    'interface': {'path': 'zope.interface.common.mapping.IEnumerableMapping',
                  'url': 'zope.interface.common.mapping.IEnumerableMapping'},
    'name': 'values',
    'read_perm': 'zope.Public',
    'signature': '()',
    'write_perm': 'n/a'}]

:meth:`class_.ClassDetails.getDoc`
----------------------------------

Get the doc string of the class STX formatted.

  >>> print(details.getDoc()[:-1])
  <p>Represent the code browser documentation root</p>


Function Details
================

This is the same deal as before, use the path to generate the function
documentation component:

  >>> details = browser.function.FunctionDetails()
  >>> details.context = traverse(cm,
  ...     'zope/app/apidoc/codemodule/browser/tests/foo')
  >>> details.request = TestRequest()

Here are the methods:

:meth:`function.FunctionDetails.getDocString`
---------------------------------------------

Get the doc string of the function in a rendered format.

  >>> details.getDocString()
  '<p>This is the foo function.</p>\n'

:meth:`function.FunctionDetails.getAttributes`
----------------------------------------------

Get all attributes of this function.

  >>> attr = details.getAttributes()[0]
  >>> pprint(attr)
  {'name': 'deprecated',
   'type': 'bool',
   'type_link': 'builtins/bool',
   'value': 'True'}

:meth:`function.FunctionDetails.getBaseURL`
-------------------------------------------

Return the URL for the API Documentation Tool.

  >>> details.getBaseURL()
  'http://127.0.0.1/++apidoc++'


Text File Details
=================

This is the same deal as before, use the path to generate the
:class:`text file documentation component <text.TextFileDetails>`:

  >>> details = browser.text.TextFileDetails()
  >>> details.context = traverse(cm,
  ...     'zope/app/apidoc/codemodule/README.rst')
  >>> details.request = TestRequest()

Here are the methods:

:meth:`text.TextFileDetails.renderedContent`
--------------------------------------------

Render the file content to HTML.

  >>> print(details.renderedContent()[:48])
  <h1 class="title">Code Documentation Module</h1>


ZCML File and Directive Details
===============================

The ZCML :class:`file details <zcml.DirectiveDetails>` are a bit
different, since there is no view class for ZCML files, just a
template. The template then uses the directive details to provide all
the view content:

  >>> details = browser.zcml.DirectiveDetails()
  >>> zcml = traverse(cm, 'zope/app/apidoc/codemodule/configure.zcml')
  >>> details.context = zcml.rootElement
  >>> details.request = TestRequest()
  >>> details.__parent__ = details.context

Here are the methods for the directive details:

:meth:`zcml.DirectiveDetails.fullTagName`
-----------------------------------------

Return the name of the directive, including prefix, if applicable.

  >>> details.fullTagName()
  'configure'

:meth:`zcml.DirectiveDetails.line`
----------------------------------

Return the line (as a string) at which this directive starts.

  >>> details.line()
  '1'

:meth:`zcml.DirectiveDetails.highlight`
---------------------------------------

It is possible to highlight a directive by passing the `line` variable as a
request variable. If the value of `line` matches the output of `line()`, this
method returns 'highlight' and otherwise ''. 'highlight' is a CSS class that
places a colored box around the directive.

  >>> details.highlight()
  ''

  >>> details.request = TestRequest(line='1')
  >>> details.highlight()
  'highlight'

:meth:`zcml.DirectiveDetails.url`
---------------------------------

Returns the URL of the directive docuemntation in the ZCML documentation
module.

  >>> details.url()
  'http://127.0.0.1/++apidoc++/ZCML/ALL/configure/index.html'

:meth:`zcml.DirectiveDetails.objectURL`
---------------------------------------

This method converts the string value of the field to an object and then
crafts a documentation URL for it:

  >>> from zope.configuration.fields import GlobalObject
  >>> field = GlobalObject()

  >>> details.objectURL('.interfaces.IZCMLFile', field, '')
  'http://127.0.0.1/++apidoc++/Interface/zope.app.apidoc.codemodule.interfaces.IZCMLFile/index.html'

  >>> details.objectURL('.zcml.ZCMLFile', field, '')
  '/zope/app/apidoc/codemodule/zcml/ZCMLFile/index.html'

:meth:`zcml.DirectiveDetails.attributes`
----------------------------------------

Returns a list of info dictionaries representing all the attributes in the
directive. If the directive is the root directive, all namespace declarations
will be listed too.

  >>> pprint(details.attributes())
  [{'name': 'xmlns',
    'url': None,
    'value': 'http://namespaces.zope.org/zope',
    'values': []},
   {'name': 'xmlns:apidoc',
    'url': None,
    'value': 'http://namespaces.zope.org/apidoc',
    'values': []},
   {'name': 'xmlns:browser',
    'url': None,
    'value': 'http://namespaces.zope.org/browser',
    'values': []}]

  >>> details.context = details.context.subs[0]
  >>> pprint(details.attributes())
  [{'name': 'class',
    'url': 'http://127.0.0.1/++apidoc++/Code/zope/app/apidoc/codemodule/module/Module/index.html',
    'value': '.module.Module',
    'values': []}]

:meth:`zcml.DirectiveDetails.hasSubDirectives`
----------------------------------------------

Returns `True`, if the directive has subdirectives; otherwise `False` is
returned.

  >>> details.hasSubDirectives()
  True

:meth:`zcml.DirectiveDetails.getElements`
-----------------------------------------

Returns a list of all sub-directives:

  >>> details.getElements()
  [<Directive ('http://namespaces.zope.org/zope', 'allow')>]

Other Examples
--------------

Let's look at sub-directive that has a namespace:

  >>> details = browser.zcml.DirectiveDetails()
  >>> zcml = traverse(cm, 'zope/app/apidoc/ftesting-base.zcml')
  >>> browser_directive = [x for x in zcml.rootElement.subs if x.name[0].endswith('browser')][0]
  >>> details.context = browser_directive
  >>> details.request = TestRequest()
  >>> details.fullTagName()
  'browser:menu'

The exact URL will vary depending on what ZCML has been loaded.

  >>> details.url()
  'http://127.0.0.1/++apidoc++/.../menu/index.html'

Now one that has some tokens:

  >>> details = browser.zcml.DirectiveDetails()
  >>> zcml = traverse(cm, 'zope/app/apidoc/enabled.zcml')
  >>> adapter_directive = [x for x in zcml.rootElement.subs if x.name[1] == 'adapter'][0]
  >>> details.context = adapter_directive
  >>> details.__parent__ = details.context
  >>> details.request = TestRequest()
  >>> pprint(details.attributes())
  [{'name': 'factory',
    'url': 'http://127.0.0.1/++apidoc++/Code/zope/app/apidoc/apidoc/apidocNamespace/index.html',
    'value': '.apidoc.apidocNamespace',
    'values': []},
   {'name': 'provides',
   'url': 'http://127.0.0.1/++apidoc++/Interface/zope.traversing.interfaces.ITraversable/index.html',
   'value': 'zope.traversing.interfaces.ITraversable',
   'values': []},
   {'name': 'for', 'url': None, 'value': '*', 'values': []},
   {'name': 'name', 'url': None, 'value': 'apidoc', 'values': []}]

Now one with *multiple* tokens:

  >>> details = browser.zcml.DirectiveDetails()
  >>> zcml = traverse(cm, 'zope/traversing/configure.zcml')
  >>> adapter_directive = [x for x in zcml.rootElement.subs if x.name[1] == 'adapter']
  >>> adapter_directive = [x for x in adapter_directive if ' ' in x.attrs[(None, 'for')]][0]
  >>> details.context = adapter_directive
  >>> details.__parent__ = details.context
  >>> details.request = TestRequest()
  >>> pprint(details.attributes())
  [{'name': 'factory',
    'url': 'http://127.0.0.1/++apidoc++/Code/zope/traversing/namespace/etc/index.html',
    'value': 'zope.traversing.namespace.etc',
    'values': []},
   {'name': 'provides',
    'url': 'http://127.0.0.1/++apidoc++/Interface/zope.traversing.interfaces.ITraversable/index.html',
    'value': 'zope.traversing.interfaces.ITraversable',
    'values': []},
   {'name': 'for',
    'url': None,
    'value': '* zope.publisher.interfaces.IRequest',
    'values': [{'url': None, 'value': '*'},
                {'url': 'http://127.0.0.1/++apidoc++/Interface/zope.publisher.interfaces.IRequest/index.html',
                 'value': 'zope.publisher.interfaces.IRequest'}]},
   {'name': 'name', 'url': None, 'value': 'etc', 'values': []}]

And now one that is subdirectives:

  >>> details = browser.zcml.DirectiveDetails()
  >>> zcml = traverse(cm, 'zope/app/apidoc/browser/configure.zcml')
  >>> adapter_directive = [x for x in zcml.rootElement.subs if x.name[1] == 'pages'][0]
  >>> details.context = adapter_directive.subs[0]
  >>> details.__parent__ = details.context
  >>> details.request = TestRequest()
  >>> details.url()
  'http://127.0.0.1/++apidoc++/.../pages/index.html#page'



The Introspector
================

There are several tools that are used to support the :mod:`introspector`.

  >>> from zope.app.apidoc.codemodule.browser import introspector

.. currentmodule:: zope.app.apidoc.codemodule.browser.introspector

:func:`getTypeLink`
-------------------

This little helper function returns the path to the type class:

  >>> from zope.app.apidoc.apidoc import APIDocumentation
  >>> introspector.getTypeLink(APIDocumentation)
  'zope/app/apidoc/apidoc/APIDocumentation'

  >>> introspector.getTypeLink(dict)
  'builtins/dict'

  >>> introspector.getTypeLink(type(None)) is None
  True

``++annotations++`` Namespace
-----------------------------

This :func:`namespace <annotationsNamespace>` is used to traverse into
the annotations of an object.

  >>> import zope.interface
  >>> from zope.annotation.interfaces import IAttributeAnnotatable

  >>> @zope.interface.implementer(IAttributeAnnotatable)
  ... class Sample(object):
  ...    pass

  >>> sample = Sample()
  >>> sample.__annotations__ = {'zope.my.namespace': 'Hello there!'}

  >>> ns = introspector.annotationsNamespace(sample)
  >>> ns.traverse('zope.my.namespace', None)
  'Hello there!'

  >>> ns.traverse('zope.my.unknown', None)
  Traceback (most recent call last):
  ...
  KeyError: 'zope.my.unknown'

Mapping ``++items++`` namespace
-------------------------------

This :func:`namespace <mappingItemsNamespace>` allows us to traverse
the items of any mapping:

  >>> ns = introspector.mappingItemsNamespace({'mykey': 'myvalue'})
  >>> ns.traverse('mykey', None)
  'myvalue'

  >>> ns.traverse('unknown', None)
  Traceback (most recent call last):
  ...
  KeyError: 'unknown'


Sequence ``++items++`` namespace
--------------------------------

This :func:`namespace <sequenceItemsNamespace>` allows us to traverse
the items of any sequence:

  >>> ns = introspector.sequenceItemsNamespace(['value1', 'value2'])
  >>> ns.traverse('0', None)
  'value1'

  >>> ns.traverse('2', None)
  Traceback (most recent call last):
  ...
  IndexError: list index out of range

  >>> ns.traverse('text', None)
  Traceback (most recent call last):
  ...
  ValueError: invalid literal for int() with base 10: 'text'

Introspector View
-----------------

The main contents of the introspector view comes from the
:class:`introspector view class <Introspector>`. In the following
section we are going to demonstrate the methods used to collect the
data. First we need to create an object though; let's use a root
folder:

  >>> rootFolder
  <...Folder object at ...>

Now we instantiate the view

  >>> from zope.publisher.browser import TestRequest
  >>> request = TestRequest()
  >>> inspect = introspector.Introspector(rootFolder, request)

so that we can start looking at the methods. First we should note that the
class documentation view is directly available:

  >>> inspect.klassView
  <zope.browserpage.simpleviewclass.SimpleViewClass from ...>
  >>> inspect.klassView.context
  <zope.app.apidoc.codemodule.class_.Class object at ...>

You can get the parent of the inspected object, which is ``None`` for the root
folder:

  >>> inspect.parent() is None
  True

You can also get the base URL of the request:

  >>> inspect.getBaseURL()
  'http://127.0.0.1/++apidoc++'

Next you can get a list of all directly provided interfaces:

  >>> ifaces = inspect.getDirectlyProvidedInterfaces()
  >>> sorted(ifaces)
  ['zope.component.interfaces.ISite', 'zope.site.interfaces.IRootFolder']

The ``getProvidedInterfaces()`` and ``getBases()`` method simply forwards its
request to the class documentation view. Thus the next method is
``getAttributes()``, which collects all sorts of useful information about the
object's attributes:

  >>> pprint(list(inspect.getAttributes()))
  [{'interface': None,
    'name': 'data',
    'read_perm': 'n/a',
    'type': 'OOBTree',
    'type_link': 'BTrees/OOBTree/OOBTree',
    'value': '<BTrees.OOBTree.OOBTree object at ...>',
    'value_linkable': True,
    'write_perm': 'n/a'}]

Of course, the methods are listed as well:

  >>> pprint(list(inspect.getMethods()))
  [...
   {'doc': '',
    'interface': 'zope.component.interfaces.IPossibleSite',
    'name': 'getSiteManager',
    'read_perm': 'zope.Public',
    'signature': '()',
    'write_perm': 'n/a'},
   ...
   {'doc': '',
    'interface': 'zope.container.interfaces.IBTreeContainer',
    'name': 'keys',
    'read_perm': 'zope.View',
    'signature': '(key=None)',
    'write_perm': 'n/a'},
   {'doc': '',
    'interface': 'zope.component.interfaces.IPossibleSite',
    'name': 'setSiteManager',
    'read_perm': 'zope.ManageServices',
    'signature': '(sm)',
    'write_perm': 'n/a'},
   ...]

The final methods deal with inspecting the objects data further. For exmaple,
if we inspect a sequence,

  >>> from persistent.list import PersistentList
  >>> list = PersistentList(['one', 'two'])

  >>> from zope.interface.common.sequence import IExtendedReadSequence
  >>> zope.interface.directlyProvides(list, IExtendedReadSequence)

  >>> inspect2 = introspector.Introspector(list, request)

we can first determine whether it really is a sequence

  >>> inspect2.isSequence()
  True

and then get the sequence items:

  >>> pprint(inspect2.getSequenceItems())
  [{'index': 0,
    'value': "'one'",
    'value_type': 'str',
    'value_type_link': 'builtins/str'},
   {'index': 1,
    'value': "'two'",
    'value_type': 'str',
    'value_type_link': 'builtins/str'}]

Similar functionality exists for a mapping. But we first have to add an item:

  >>> rootFolder['list'] = list

Now let's have a look:

  >>> inspect.isMapping()
  True

  >>> pprint(inspect.getMappingItems())
  [...
   {'key': 'list',
    'key_string': "'list'",
    'value': "['one', 'two']",
    'value_type': 'ContainedProxy',
    'value_type_link': 'zope/container/contained/ContainedProxy'},
  ...]

The final two methods doeal with the introspection of the annotations. If an
object is annotatable,

  >>> inspect.isAnnotatable()
  True

then we can get an annotation mapping:

  >>> rootFolder.__annotations__ = {'my.list': list}

  >>> pprint(inspect.getAnnotationsInfo())
  [{'key': 'my.list',
    'key_string': "'my.list'",
    'value': "['one', 'two']",
    'value_type': 'PersistentList',
    'value_type_link': 'persistent/list/PersistentList'}]

And that's it. Fur some browser-based demonstration see :doc:`codemodule_browser_introspector`.
