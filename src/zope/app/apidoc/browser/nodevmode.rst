=========================================
 API doc when developer mode is disabled
=========================================

The API docs should not be exposed to anybody as they allow introspection of
code and files on the file system that should not be exposed through the web.

In this test case, the developer mode was disabled, so we will only see a page
informing the user that the API docs are disabled. We do this as we changed
the default during the release of Zope 3.3 and many developers will still
assume that their instances are running in developer mode, while they aren't.

  >>> from zope.testbrowser.wsgi import Browser
  >>> browser = Browser()
  >>> browser.handleErrors = False
  >>> browser.addHeader('Authorization', 'Basic mgr:mgrpw')
  >>> browser.open("http://localhost/++apidoc++")
  >>> browser.contents
  '...API documentation is disabled...'
