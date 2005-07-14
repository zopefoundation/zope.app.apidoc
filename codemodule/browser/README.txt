====================================
Code Browser Presentation Components
====================================

This document describes the API of the views complementing the varius code
browser documentation components. The views can be found in

  >>> from zope.app.apidoc.codemodule import browser

We will also need the code browser documentation module:

  >>> from zope.app import zapi
  >>> from zope.app.apidoc.interfaces import IDocumentationModule
  >>> cm = zapi.getUtility(IDocumentationModule, 'Code')

The `zope` package is already registered and available with the code module.


Module Details
--------------

The module details are easily created, since we can just use the traversal
process to get a module documentation object:

  >>> details = browser.module.ModuleDetails()
  >>> details.context = zapi.traverse(cm, 
  ...     'zope/app/apidoc/codemodule/codemodule')
  >>> from zope.publisher.browser import TestRequest
  >>> details.request = TestRequest()

`getDoc()`
~~~~~~~~~~

Get the doc string of the module formatted in STX or ReST.

  >>> print details.getDoc().strip()
  <p>Code Documentation Module</p>
  <p>This module is able to take a dotted name of any class and display
  documentation for it.</p>

`getEntries(columns=True)`
~~~~~~~~~~~~~~~~~~~~~~~~~~

Return info objects for all modules and classes in this module.

  >>> pprint(details.getEntries(False))
  [{'isclass': True,
    'isfunction': False,
    'isinterface': False,
    'ismodule': False,
    'istextfile': False,
    'iszcmlfile': False,
    'name': 'CodeModule',
    'url': 'http://127.0.0.1/zope/app/apidoc/codemodule/codemodule/CodeModule'}]

`getBreadCrumbs()`
~~~~~~~~~~~~~~~~~~

Create breadcrumbs for the module path.

We cannot reuse the the system's bread crumbs, since they go all the
way up to the root, but we just want to go to the root module.

  >>> pprint(details.getBreadCrumbs())
  [{'name': u'[top]',
    'url': 'http://127.0.0.1'},
   {'name': u'zope',
    'url': 'http://127.0.0.1/zope'},
   {'name': 'app',
    'url': 'http://127.0.0.1/zope/app'},
   {'name': 'apidoc',
    'url': 'http://127.0.0.1/zope/app/apidoc'},
   {'name': 'codemodule',
    'url': 'http://127.0.0.1/zope/app/apidoc/codemodule'},
   {'name': 'codemodule',
    'url': 'http://127.0.0.1/zope/app/apidoc/codemodule/codemodule'}]


Class Details
-------------

The class details are easily created, since we can just use the traversal
process to get a class documentation object:

  >>> details = browser.class_.ClassDetails()
  >>> details.context = zapi.traverse(
  ...     cm, 'zope/app/apidoc/codemodule/codemodule/CodeModule')

  >>> details.request = TestRequest()

Now that we have the details class we can just access the various methods:

`getBases()`
~~~~~~~~~~~

Get all bases of this class.

  >>> pprint(details.getBases())
  [{'path': 'zope.app.apidoc.codemodule.module.Module',
    'url': 'http://127.0.0.1/zope/app/apidoc/codemodule/module/Module'}]

`getKnownSubclasses()`
~~~~~~~~~~~~~~~~~~~~~~
Get all known subclasses of this class.

  >>> details.getKnownSubclasses()
  []

`_listClasses(classes)`
~~~~~~~~~~~~~~~~~~~~~~~

Prepare a list of classes for presentation.

  >>> import zope.app.apidoc.apidoc
  >>> import zope.app.apidoc.codemodule.codemodule

  >>> pprint(details._listClasses([
  ...       zope.app.apidoc.apidoc.APIDocumentation,
  ...       zope.app.apidoc.codemodule.codemodule.Module]))
  [{'path': 'zope.app.apidoc.apidoc.APIDocumentation',
    'url': 'http://127.0.0.1/zope/app/apidoc/apidoc/APIDocumentation'},
   {'path': 'zope.app.apidoc.codemodule.module.Module',
    'url': 'http://127.0.0.1/zope/app/apidoc/codemodule/module/Module'}]

`getBaseURL()`
~~~~~~~~~~~~~~

Return the URL for the API Documentation Tool.

Note that the following output is a bit different than usual, since
we have not setup all path elements.

  >>> details.getBaseURL()
  'http://127.0.0.1'

`getInterfaces()`
~~~~~~~~~~~~~~~~~

Get all implemented interfaces (as paths) of this class.

  >>> pprint(details.getInterfaces())
  ['zope.app.apidoc.interfaces.IDocumentationModule',
   'zope.app.location.interfaces.ILocation',
   'zope.app.apidoc.codemodule.interfaces.IModuleDocumentation',
   'zope.app.container.interfaces.IReadContainer']

`getAttributes()`
~~~~~~~~~~~~~~~~~

Get all attributes of this class.

  >>> pprint(details.getAttributes()[1])
  {'interface': 'zope.app.apidoc.interfaces.IDocumentationModule',
   'name': 'title',
   'read_perm': None,
   'type': 'MessageID',
   'type_link': 'zope/i18nmessageid/messageid/MessageID',
   'value': "u'Code Browser'",
   'write_perm': None}

`getMethods()`
~~~~~~~~~~~~~~
Get all methods of this class.

  >>> pprint(details.getMethods()[-2:])
  [{'doc': u'<p>Setup module and class tree.</p>\n',
    'interface': None,
    'name': 'setup',
    'read_perm': None,
    'signature': '()',
    'write_perm': None},
   {'doc': u'',
    'interface': 'zope.interface.common.mapping.IEnumerableMapping',
    'name': 'values',
    'read_perm': None,
    'signature': '()',
    'write_perm': None}]

`getDoc()`
~~~~~~~~~~

Get the doc string of the class STX formatted.

  >>> print details.getDoc()[:-1]
  <p>Represent the code browser documentation root</p>


Function Details
----------------

This is the same deal as before, use the path to generate the function
documentation component:

  >>> details = browser.function.FunctionDetails()
  >>> details.context = zapi.traverse(cm, 
  ...     'zope/app/apidoc/codemodule/browser/tests/foo')
  >>> details.request = TestRequest()

Here are the methods:

`getDocString()`
~~~~~~~~~~~~~~~~

Get the doc string of the function in a rendered format.

  >>> details.getDocString()
  u'<p>This is the foo function.</p>\n'

`getAttributes()`
~~~~~~~~~~~~~~~~~

Get all attributes of this function.

  >>> attr = details.getAttributes()[0]
  >>> pprint(attr)
  {'name': 'deprecated',
   'type': 'bool',
   'type_link': '__builtin__/bool',
   'value': 'True'}


Text File Details
-----------------

This is the same deal as before, use the path to generate the text file
documentation component:

  >>> details = browser.text.TextFileDetails()
  >>> details.context = zapi.traverse(cm, 
  ...     'zope/app/apidoc/codemodule/README.txt')
  >>> details.request = TestRequest()

Here are the methods:

`renderedContent()`
~~~~~~~~~~~~~~~~~~~

Render the file content to HTML.

  >>> print details.renderedContent()[:48]
  <h1 class="title">Code Documentation Module</h1>


ZCML File and Directive Details
-------------------------------

The ZCML file details are a bit different, since there is no view class for
ZCML files, just a template. The template then uses the directive details to
provide all the view content:

  >>> details = browser.zcml.DirectiveDetails()
  >>> zcml = zapi.traverse(cm, 
  ...     'zope/app/apidoc/codemodule/configure.zcml')
  >>> details.context = zcml.rootElement
  >>> details.request = TestRequest()
  >>> details.__parent__ = details.context

Here are the methods for the directive details:

`fullTagName()`
~~~~~~~~~~~~~~~

Return the name of the directive, including prefix, if applicable.

  >>> details.fullTagName()
  u'configure'

`line()`
~~~~~~~~

Return the line (as a string) at which this directive starts.

  >>> details.line()
  '1'

`highlight()`
~~~~~~~~~~~~~

It is possible to highlight a directive by passing the `line` variable as a
request variable. If the value of `line` matches the output of `line()`, this
method returns 'highlight' and otherwise ''. 'highlight' is a CSS class that
places a colored box around the directive.

  >>> details.highlight()
  ''

  >>> details.request = TestRequest(line='1')
  >>> details.highlight()
  'highlight'

`url()`
~~~~~~~

Returns the URL of the directive docuemntation in the ZCML documentation
module.

  >>> details.url()
  u'http://127.0.0.1/../ZCML/ALL/configure/index.html'

The result is a bit strange, since the ZCML Documentation module is the
containment root.

`ifaceURL(value, field, rootURL)`
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

This method converts the string value of the field to an interface and then
crafts a documentation URL for it:

  >>> from zope.configuration.fields import GlobalInterface
  >>> field = GlobalInterface()

  >>> details.ifaceURL('.interfaces.IZCMLFile', field, '')
  '/../Interface/zope.app.apidoc.codemodule.interfaces.IZCMLFile/apiindex.html'

`objectURL(value, field, rootURL)`
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

This method converts the string value of the field to an object and then
crafts a documentation URL for it:

  >>> from zope.configuration.fields import GlobalObject
  >>> field = GlobalObject()

  >>> details.objectURL('.interfaces.IZCMLFile', field, '')
  '/../Interface/zope.app.apidoc.codemodule.interfaces.IZCMLFile/apiindex.html'

  >>> details.objectURL('.zcml.ZCMLFile', field, '')
  '/zope/app/apidoc/codemodule/zcml/ZCMLFile/index.html'

`attributes()`
~~~~~~~~~~~~~~

Returns a list of info dictionaries representing all the attributes in the
directive. If the directive is the root directive, all namespace declarations
will be listed too.

  >>> pprint(details.attributes())
  [{'name': 'xmlns',
    'url': None,
    'value': u'http://namespaces.zope.org/zope',
    'values': []},
   {'name': u'xmlns:apidoc',
    'url': None,
    'value': u'http://namespaces.zope.org/apidoc',
    'values': []},
   {'name': u'xmlns:browser',
    'url': None,
    'value': u'http://namespaces.zope.org/browser',
    'values': []}]

  >>> details.context = details.context.subs[0]
  >>> pprint(details.attributes())
  [{'name': u'class',
    'url': 
        'http://127.0.0.1/zope/app/apidoc/codemodule/module/Module/index.html',
    'value': u'.module.Module',
    'values': []}]

`hasSubDirectives()`
~~~~~~~~~~~~~~~~~~~~

Returns `True`, if the directive has subdirectives; otherwise `False` is
returned.

  >>> details.hasSubDirectives() 
  True

`getElements()`
~~~~~~~~~~~~~~~

Returns a list of all sub-directives:

  >>> details.getElements()
  [<Directive (u'http://namespaces.zope.org/zope', u'allow')>]
 

The Introspector View
---------------------

In order to allow the quick lookup of documentation from the content
components themselves, a special "Introspector" tab is added for all content
types. When clicked, it will forward you to the appropriate code browser
documentation screen. 

So for a given content type:

  >>> class Content(object):
  ...    pass

  >>> Content.__module__ = 'module.name.here'

we can generate the introspector redirector like this:

  >>> from zope.app.apidoc.codemodule.browser import introspector
  >>> request = TestRequest()
  >>> view = introspector.Introspector(Content(), request)
  >>> view.class_name()
  'module.name.here.Content'
  >>> view.class_url()
  'http://127.0.0.1/++apidoc++/Code/module/name/here/Content/index.html'
  >>> view.direct_interfaces()
  []

If the instance directly provides any interfaces, these are reported
as well:

  >>> import zope.interface
  >>> zope.interface.directlyProvides(view.context,
  ...                                 IDocumentationModule)
  >>> pprint(view.direct_interfaces())
  [{'module': 'zope.app.apidoc.interfaces',
    'name': 'IDocumentationModule',
    'url': 'http://127.0.0.1/++apidoc++/Interface/zope.app.apidoc.interfaces.IDocumentationModule/apiindex.html'}]
