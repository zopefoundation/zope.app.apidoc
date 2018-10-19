========================
Object Introspector View
========================

The "Introspector" view provides access to information about the current
obejct, the context of the introspector view. When in ``devmode``, the
introspector is simply available as follows:

    >>> from zope.testbrowser.wsgi import Browser
    >>> browser = Browser()
    >>> browser.addHeader('Authorization', 'Basic mgr:mgrpw')
    >>> browser.handleErrors = False
    >>> browser.open('http://localhost/manage')
    >>> browser.getLink('Introspector').click()

The page starts with telling you the class/type

    >>> browser.getLink('zope.site.folder.Folder').url
    'http://localhost/++apidoc++/Code/zope/site/folder/Folder/index.html'

and the name of the object:

    >>> '&lt;no name&gt;' in browser.contents
    True

Of course, the root folder does not have a name. As you can see the type links
directly to the API documentation of the class.

The next section lists all directly provided interfaces. The root
folder directly provides the :class:`zope.site.interfaces.ISite` and
:class:`zope.site.interfaces.IRootFolder` interface, so we should see
those:

    >>> browser.getLink('zope.component.interfaces.ISite').url
    '.../++apidoc++/Interface/zope.component.interfaces.ISite/index.html'
    >>> browser.getLink('zope.site.interfaces.IRootFolder').url
    '...apidoc++/Interface/zope.site.interfaces.IRootFolder/index.html'

The next two section, the implemented interfaces and the base classes,
are not instance specific pieces of information, but they are still
nice to see at this point. For example, a
:class:`zope.site.folder.Folder` instance provides the following
interfaces:

    >>> browser.getLink('zope.site.interfaces.IFolder').url
    '.../++apidoc++/Interface/zope.site.interfaces.IFolder/index.html'
    >>> browser.getLink('persistent.interfaces.IPersistent').url
    '.../++apidoc++/Interface/persistent.interfaces.IPersistent/index.html'
    >>> browser.getLink('zope.component.interfaces.IPossibleSite').url
    '.../Interface/zope.component.interfaces.IPossibleSite/index.html'
    >>> browser.getLink('zope.location.interfaces.IContained').url
    '...doc++/Interface/zope.location.interfaces.IContained/index.html'

The base classes of the ``Folder`` are as follows:

    >>> browser.getLink('zope.site.site.SiteManagerContainer').url
    '...apidoc++/Code/zope/site/site/SiteManagerContainer/index.html'

Now that we described the component and class level of the object, the view
dives into some details. First it lists the attributes/properties of the
object, including the value of the attribute. This is information can be very
useful when debugging an application. The only attribute of the folder is the
data attribute:

    >>> print(browser.contents)
    <!DOCTYPE...
    ...
    <h2>Attributes/Properties</h2>
    <div class="indent">
    <ul class="attr-list">
      <li>
        <b><code>data</code></b>
        ...
        <br />
        <i>Value:</i>
        <a href="http://localhost/++attribute++data/@@introspector.html">
        <code>&lt;BTrees.OOBTree.OOBTree object at ...&gt;</code>
        </a>
        <br />
        <span class="small">
          <i>Permissions:</i>
          n/a
              <span>(read)</span>,
          n/a
              <span>(write)</span>
        </span>
      </li>
    </ul>
    </div>
    ...

There are, however, several methods since the full mapping interface is
implemented. Like for the class method documentation, the method's signature,
doc string, permissions and the interface the method is declared in. Here an
example:

    >>> print(browser.contents)
    <!DOCTYPE...
    ...
    <h2>Methods</h2>
    <div class="indent">
    <ul class="attr-list">
      <li>
        <b><code>get(key, default=None)</code>
        </b><br />
        <div class="inline documentation"><p>See interface <cite>IReadContainer</cite></p>
        </div>
        <span class="small">
          <i>Interface:</i>
          <a href="...">zope.interface.common.mapping.IReadMapping</a><br />
        </span>
        <span class="small">
          <i>Permissions:</i>
          zope.View
              <span>(read)</span>,
          n/a
              <span>(write)</span>
        </span>
      </li>
      ...
    </ul>
    </div>
    ...

Towards the bottom of the page, there are some optional sections. Some
objects, for example our root folder, are inheritely mappings or
sequences. Their data then is often hard to see in the attributes section, so
they are provided in a aseparate section. To see anything useful, we have to
add an object to the folder first:

    >>> import re
    >>> browser.getLink(re.compile('^File$')).click()
    >>> from io import BytesIO
    >>> browser.getControl('Data').value = BytesIO(b'content')
    >>> browser.getControl(name='add_input_name').value = 'file.txt'
    >>> browser.getControl('Add').click()
    >>> browser.getLink('Introspector').click()

Now the introspector will show the file and allow you to click on it:

    >>> print(browser.contents)
    <!DOCTYPE...
    ...
      <div>
        <h2>Mapping Items</h2>
        <div class="indent">
          <ul class="attr-list">
            <li>
              <b>
                <code>'file.txt'</code>
              </b>
              <br />
              <a href="++items++file.txt/@@introspector.html">
                <code>&lt;...File object at ...&gt;</code>
              </a>
                (<span>type:</span>
                <a href="http://localhost/++apidoc++/Code/zope/container/contained/ContainedProxy/index.html">
                  <code>ContainedProxy</code></a>)
    ...

The final section of the introspector displays the annotations that are
declared for the object. The standard annotation that almost every object
provides is the Dublin Core:

    >>> print(browser.contents)
    <!DOCTYPE...
    ...
    <h2>Annotations</h2>
        <div class="indent">
          <ul class="attr-list">
            <li>
              <b>
                <code>'zope.app.dublincore.ZopeDublinCore'</code>
              </b>
              <br />
              <a href="++annotations++zope.app.dublincore.ZopeDublinCore/@@introspector.html">
                <code>...</code>
              </a>
                (<span>type:</span>
                <a href="http://localhost/++apidoc++/Code/zope/dublincore/annotatableadapter/ZDCAnnotationData/index.html">
                  <code>ZDCAnnotationData</code></a>)
            </li>
          </ul>
        </div>
      </div>
    <BLANKLINE>
    </div>
    ...

As you can see you can click on the annotation to discover it further;
the exact constructor signature varies depending on Python version
(some versions report ``*args, **kwargs``, others report ``dict=None,
**kwargs``):

    >>> browser.getLink('ZDCAnnotationData').click()
    >>> print(browser.contents)
    <!DOCTYPE...
    ...
      <h2 ...>Constructor</h2>
      <div class="indent">
        <div>
          <b><code>__init__(..., **kwargs)</code>
          </b><br />
          <div class="inline documentation"></div>
        </div>
    ...

That's it! The introspector view has a lot more potential, but that's for
someone else to do.
