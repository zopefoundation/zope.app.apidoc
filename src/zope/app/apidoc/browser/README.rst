=====================
Generic API Doc Views
=====================

Get a browser started:

  >>> from zope.testbrowser.wsgi import Browser
  >>> browser = Browser()
  >>> browser.addHeader('Authorization', 'Basic mgr:mgrpw')


Not Found View
--------------

The `APIDOC` skin defines a custom not found view, since it fits the look and
feel better and does not have all the O-wrap clutter:

  >>> browser.open('http://localhost/++apidoc++/non-existent/')
  Traceback (most recent call last):
  ...
  urllib.error.HTTPError: HTTP Error 404: Not Found

  >>> try:
  ...     browser.open('http://localhost/++apidoc++/non-existent/')
  ... except Exception:
  ...     pass

  >>> print(browser.contents)
  <...
  <h1 class="details-header">
    Page Not Found
  </h1>
  <BLANKLINE>
  <p>
    While broken links occur occassionally, they are considered bugs. Please
    report any broken link to
    <a href="mailto:zope-dev@zope.org">zope-dev@zope.org</a>.
  </p>
  ...

Preferences
-----------

The ``APIDOC`` skin also does the same for editing preference groups:

  >>> browser.open('http://localhost/++preferences++apidoc/InterfaceDetails/apidocIndex.html')
  >>> print(browser.contents)
  <...
  <div class="documentation"><p>Preferences for API Docs' Interface Details Screen</p>
  ...
