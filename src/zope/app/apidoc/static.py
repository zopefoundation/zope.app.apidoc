##############################################################################
#
# Copyright (c) 2005 Zope Foundation and Contributors.
# All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
##############################################################################
"""Retrieve Static APIDOC


"""
__docformat__ = "reStructuredText"

import base64
import os
import os.path
import sys
import time
import argparse
from six.moves.urllib import error as urllib2
from six.moves.urllib import parse as urlparse

import warnings

import zope.testbrowser.browser
import zope.testbrowser.wsgi


from zope.app.apidoc import classregistry

VERBOSITY_MAP = {1: 'ERROR', 2: 'WARNING', 3: 'INFO'}

# A mapping of HTML elements that can contain links to the attribute that
# actually contains the link, with the exception of standard <a> tags.
urltags = {
    "area": "href",
    "base": "href",
    "frame": "src",
    "iframe": "src",
    "link": "href",
    "img": "src",
    "script": "src",
}

def getMaxWidth():
    try:
        import curses
    except ImportError: # pragma: no cover
        pass
    else:
        try:
            curses.setupterm()
            cols = curses.tigetnum('cols')
            if cols > 0:
                return cols
        except curses.error: # pragma: no cover
            pass
    return 80 # pragma: no cover

def cleanURL(url):
    """Clean a URL from parameters."""
    if '?' in url:
        url = url.split('?')[0]
    if '#' in url:
        url = url.split('#')[0]

    fragments = list(urlparse.urlparse(url))

    fragments[2] = os.path.normpath(fragments[2])
    fragments[2].replace('//', '/')
    norm = urlparse.urlunparse(fragments)
    return norm



def completeURL(url):
    """Add file to URL, if not provided."""
    if url.endswith('/'):
        url += 'index.html'
    if '.' not in url.split('/')[-1]:
        url += '/index.html'

    fragments = list(urlparse.urlparse(url))
    fragments[2] = os.path.normpath(fragments[2])
    return urlparse.urlunparse(fragments)


class Link(object):
    """A link in the page."""

    def __init__(self, url, rootURL, referenceURL='None'):
        self.rootURL = rootURL
        self.referenceURL = referenceURL
        self.originalURL = url

        absolute_url = urlparse.urljoin(rootURL, url)
        self.callableURL = absolute_url
        self.url = completeURL(cleanURL(url))
        self.absoluteURL = completeURL(cleanURL(self.callableURL))

    def isLocalURL(self):
        """Determine whether the passed in URL is local and accessible."""
        # Javascript function call
        if self.url.startswith('javascript:'):
            return False
        # Mail Link
        if self.url.startswith('mailto:'):
            return False
        # External Link
        if self.url.startswith('http://') and \
               not self.url.startswith(self.rootURL):
            return False
        return True

    def isApidocLink(self):
        # Make sure that only apidoc links are loaded
        allowed_prefixes = ((self.rootURL + '++apidoc++/'),
                            (self.rootURL + '@@/'))
        return self.absoluteURL.startswith(allowed_prefixes)


class OnlineBrowser(zope.testbrowser.browser.Browser):

    def setUserAndPassword(self, user, pw):
        """Specify the username and password to use for the retrieval."""
        user_pw = user + ':' + pw
        if not isinstance(user_pw, bytes):
            user_pw = user_pw.encode('utf-8')
        encoded = base64.b64encode(user_pw).strip()
        if not isinstance(encoded, str):
            encoded = encoded.decode('ascii')
        self.addHeader("Authorization", 'Basic ' + encoded)

    @classmethod
    def begin(cls):
        return cls()

    def end(self):
        pass

    def setDebugMode(self, debug):
        handle = not debug
        self.addHeader('X-zope-handle-errors', str(handle))


class PublisherBrowser(zope.testbrowser.wsgi.Browser):

    old_appsetup_context = None


    def setUserAndPassword(self, user, pw):
        """Specify the username and password to use for the retrieval."""
        self.addHeader('Authorization', 'Basic %s:%s' % (user, pw))

    @classmethod
    def begin(cls):
        # TODO: We need to let this define what config file to execute.
        from zope.app.apidoc.testing import APIDocLayer
        from zope.app.appsetup import appsetup
        APIDocLayer.setUp()
        APIDocLayer.testSetUp()

        self = cls()

        # Fix up path for tests.
        self.old_appsetup_context = appsetup.getConfigContext()
        setattr(appsetup, '__config_context', APIDocLayer.context)

        return self

    def end(self):
        from zope.app.apidoc.testing import APIDocLayer
        from zope.app.appsetup import appsetup
        APIDocLayer.testTearDown()
        APIDocLayer.tearDown()
        setattr(appsetup, '__config_context', self.old_appsetup_context)
        self.old_appsetup_context = None

    def setDebugMode(self, debug):
        self.handleErrors = not debug

class ArbitraryLink(zope.testbrowser.browser.Link):

    attr_name = 'src'

    def __init__(self, elem, browser, base, attr_name=None):
        super(ArbitraryLink, self).__init__(elem, browser, base)
        if attr_name:
            self.attr_name = attr_name

    @property
    def url(self):
        relurl = self._link[self.attr_name]
        return self.browser._absoluteUrl(relurl)

class StaticAPIDocGenerator(object):
    """Static API doc Maker"""

    counter = 0
    linkErrors = 0
    htmlErrors = 0
    otherErrors = 0
    visited = ()

    _old_ignore_modules = None
    _old_import_unknown_modules = None

    def __init__(self, options):
        self.options = options
        self.linkQueue = []

        if self.options.ret_kind == 'webserver': # pragma: no cover
            self.browser = OnlineBrowser
            self.base_url = self.options.url
            if self.base_url[-1] != '/':
                self.base_url += '/'
        else:
            assert self.options.ret_kind == 'publisher', self.options.ret_kind
            self.browser = PublisherBrowser
            self.base_url = 'http://localhost/'

        for url in self.options.additional_urls + [self.options.startpage]:
            link = Link(url, self.base_url)
            self.linkQueue.append(link)

        self.rootDir = self.options.target_dir
        self.maxWidth = getMaxWidth() - 13
        self.needNewLine = False

    def __enter__(self):
        if not os.path.exists(self.rootDir):
            os.makedirs(self.rootDir)

        self.browser = self.browser.begin()
        self.browser.setUserAndPassword(self.options.username,
                                        self.options.password)

        self.browser.setDebugMode(self.options.debug)

        self._old_ignore_modules = classregistry.IGNORE_MODULES
        classregistry.IGNORE_MODULES = set(self.options.ignore_modules)

        self._old_import_unknown_modules = classregistry.__import_unknown_modules__
        if self.options.import_unknown_modules:
            classregistry.__import_unknown_modules__ = True


    def __exit__(self, *args):
        self.browser.end()
        classregistry.IGNORE_MODULES = self._old_ignore_modules
        classregistry.__import_unknown_modules__ = self._old_import_unknown_modules

    def retrieve(self):
        """Start the retrieval of the apidoc."""
        t0 = time.time()
        end_time = None
        if self.options.max_runtime:
            end_time = t0 + self.options.max_runtime

        self.visited = set()

        # Turn off deprecation warnings
        warnings.filterwarnings("ignore", category=DeprecationWarning)


        # Work through all links until there are no more to work on.
        self.sendMessage('Starting retrieval.')
        while self.linkQueue:
            link = self.linkQueue.pop()
            # Sometimes things are placed many times into the queue, for example
            # if the same link appears twice in a page. In those cases, we can
            # check at this point whether the URL has been already handled.
            if link.absoluteURL not in self.visited:
                self.showProgress(link)
                self.processLink(link)
            if end_time and time.time() >= end_time:
                break

        t1 = time.time()

        self.sendMessage("Run time: %.3f sec" % (t1-t0))
        self.sendMessage("Links: %i" % self.counter)
        if self.linkQueue:
            self.sendMessage("Unprocessed links: %d" % len(self.linkQueue))
        self.sendMessage("Link Retrieval Errors: %i" % self.linkErrors)
        self.sendMessage("HTML ParsingErrors: %i" % self.htmlErrors)

    def showProgress(self, link):
        self.counter += 1
        if self.options.progress:
            url = link.absoluteURL[-(self.maxWidth):]
            sys.stdout.write('\r' + ' ' * (self.maxWidth + 13))
            sys.stdout.write('\rLink %5d: %s' % (self.counter, url))
            sys.stdout.flush()
            self.needNewLine = True

    def sendMessage(self, msg, verbosity=4):
        if self.options.verbosity >= verbosity:
            if self.needNewLine:
                sys.stdout.write('\n')
            sys.stdout.write(VERBOSITY_MAP.get(verbosity, 'INFO')+': ')
            sys.stdout.write(msg)
            sys.stdout.write('\n')
            sys.stdout.flush()
            self.needNewLine = False

    def processLink(self, link):
        """Process a link."""

        url = link.absoluteURL

        # Whatever will happen, we have looked at the URL
        self.visited.add(url)

        # Retrieve the content
        try:
            self.browser.open(link.callableURL)
        except urllib2.HTTPError as error:
            # Something went wrong with retrieving the page.
            self.linkErrors += 1
            self.sendMessage(
                '%s (%i): %s' % (error.msg, error.code, link.callableURL), 2)
            self.sendMessage('+-> Reference: ' + link.referenceURL, 2)
        except (urllib2.URLError, ValueError):
            # We had a bad URL running the publisher browser
            self.linkErrors += 1
            self.sendMessage('Bad URL: ' + link.callableURL, 2)
            self.sendMessage('+-> Reference: ' + link.referenceURL, 2)
        except BaseException as error:
            # This should never happen outside the debug mode. We really want
            # to catch all exceptions, so that we can investigate them.
            self.sendMessage('Bad URL: ' + link.callableURL, 2)
            self.sendMessage('+-> Reference: ' + link.referenceURL, 2)
            self.otherErrors += 1

            if self.options.debug: # pragma: no cover
                import pdb; pdb.set_trace()
            return

        self._handleOneResponse(link)

    def _handleDirForResponse(self, link):
        url = link.absoluteURL

        # Make sure the directory exists and get a file path.
        relativeURL = url.replace(self.base_url, '')
        segments = relativeURL.split('/')
        filename = segments.pop()

        dir_part = self.rootDir
        for segment in segments:
            dir_part = os.path.join(dir_part, segment)
            dir_part = os.path.normpath(dir_part)
            if not os.path.exists(dir_part):
                os.makedirs(dir_part)

        filepath = os.path.join(dir_part, filename)
        return filepath

    def _handleFindLinksForResponse(self, link):
        # Now retrieve all links and rewrite the html
        contents = self.browser.contents

        if not self.browser.isHtml:
            return contents

        url = link.absoluteURL
        html = self.browser._response.html # pylint:disable=protected-access
        baseUrl = self.browser._getBaseUrl() # pylint:disable=protected-access

        links = html.find_all('a')
        links = [zope.testbrowser.browser.Link(a, self.browser, baseUrl)
                 for a in links]

        for tagname, attrname in urltags.items():
            tags = html.find_all(tagname)
            tag_links = [ArbitraryLink(a, self.browser, baseUrl, attrname)
                         for a in tags]
            links.extend(tag_links)

        mylinks = []
        for l in links:
            try:
                mylinks.append(Link(l.url, self.base_url, url))
            except KeyError:
                # Very occasionally we get a tag that doesn't have the expected
                # attribute.
                pass
        links = mylinks

        relativeURL = url.replace(self.base_url, '')
        segments = relativeURL.split('/')
        segments.pop() # filename

        for page_link in links:
            # Make sure we do not handle unwanted links.
            if not page_link.isLocalURL() or not page_link.isApidocLink(): # pragma: no cover
                continue

            # Add link to the queue
            if page_link.absoluteURL not in self.visited:
                self.linkQueue.insert(0, page_link)

            # Rewrite URLs
            parts = ['..'] * len(segments)
            parts.append(page_link.absoluteURL.replace(self.base_url, ''))
            contents = contents.replace(page_link.originalURL, '/'.join(parts))

        return contents

    def _handleOneResponse(self, link):
        # Get the response content

        filepath = self._handleDirForResponse(link)

        contents = self._handleFindLinksForResponse(link)

        # Write the data into the file
        if not isinstance(contents, bytes):
            contents = contents.encode('utf-8')
        try:
            with open(filepath, 'wb') as f:
                f.write(contents)
        except IOError: # pragma: no cover
            # The file already exists, so it is a duplicate and a bad one,
            # since the URL misses `index.hml`. ReST can produce strange URLs
            # that produce this problem, and we have little control over it.

            # In other words, since we don't specify to open the file
            # in exclusive creation, perhaps it refers to a
            # directory? Or the disk is getting full?
            pass


###############################################################################
# Command-line UI

def _create_arg_parser():

    parser = argparse.ArgumentParser()

    parser.add_argument("target_dir",
                        help="The directory to contain the output files")

    ######################################################################
    # Retrieval

    retrieval = parser.add_argument_group(title="Retrieval",
                                          description="Options that deal with setting up the generator")

    ret_kind = retrieval.add_mutually_exclusive_group()

    ret_kind.add_argument(
        '--publisher', '-p', action="store_const", dest='ret_kind',
        const="publisher", default='publisher',
        help="""Use the publisher directly to retrieve the data. The program will bring up
        Zope 3 for you.
        """
    )

    ret_kind.add_argument(
        '--webserver', '-w', action="store_const", dest='ret_kind',
        const="webserver",
        help="""Use an external Web server that is connected to Zope 3."""
    )

    retrieval.add_argument(
        '--url', '-u', action="store", dest='url',
        default="http://localhost/",
        help="""The URL that will be used to retrieve the HTML pages. This option is
        meaningless, if you are using the publisher as backend. Also, the value of
        this option should *not* include the `++apidoc++` namespace."""
    )

    retrieval.add_argument(
        '--startpage', '-s', action="store", dest='startpage',
        default='/++apidoc++/static.html',
        help="""The startpage specifies the path (after the URL) that is used as the starting
        point to retrieve the contents. This
        option can be very useful for debugging, since it allows you to select
        specific pages. """
    )

    retrieval.add_argument(
        '--username', '--user', action="store", dest='username',
        default="mgr",
        help="""Username to access the Web site."""
    )

    retrieval.add_argument(
        '--password', '--pwd', action="store", dest='password',
        default="mgrpw",
        help="""Password to access the Web site."""
    )

    retrieval.add_argument(
        '--add', '-a', action="append", dest='additional_urls',
        nargs="*",
        default=[
            '/@@/varrow.png',
            '/@@/harrow.png',
            '/@@/tree_images/minus.png',
            '/@@/tree_images/plus.png',
            '/@@/tree_images/minus_vline.png',
            '/@@/tree_images/plus_vline.png',
        ],
        help="""Add an additional URL to the list of URLs to retrieve. Specifying those is
        sometimes necessary, if the links are hidden in cryptic Javascript code."""
    )

    retrieval.add_argument(
        '--ignore', '-i', action="append", dest='ignore_modules',
        nargs="*",
        default=['twisted', 'zope.app.twisted.ftp.test'],
        help="""Add modules that should be ignored during retrieval. That allows you to limit
        the scope of the generated API documentation."""
    )

    # XXX: How can this actually be turned off or disallowed?
    retrieval.add_argument(
        '--load-all', '-l', action="store_true", dest='import_unknown_modules',
        default=True,
        help="""Retrieve all referenced modules, even if they have not been imported during
        the startup process."""
    )

    retrieval.add_argument(
        '--max-runtime', action='store', type=int, default=0,
        help="""If given, the program will attempt to run for no longer than this
        many seconds, terminating after the time limit and leaving
        output unfinished. This is most helpful for tests."""
    )

    ######################################################################
    # Reporting

    reporting = parser.add_argument_group(title="Reporting",
                                          description="Options that configure the user output information.")

    reporting.add_argument(
        '--verbosity', '-v', type=int, dest='verbosity',
        default=5,
        help="""Specifies the reporting detail level."""
    )

    reporting.add_argument(
        '--progress', '-b', action="store_true", dest='progress',
        default=True,
        help="""Output progress status."""
    )

    reporting.add_argument(
        '--debug', '-d', action="store_true", dest='debug',
        help="""Run in debug mode. This will allow you to use the debugger, if the publisher
        experienced an error."""
    )

    return parser

######################################################################
# Command-line processing


def get_options(args=None):
    #original_testrunner_args = args

    options = _create_arg_parser().parse_args(args)

    #options.original_testrunner_args = original_testrunner_args

    return options

# Command-line UI
###############################################################################


def main(args=None, generator=StaticAPIDocGenerator):
    options = get_options(args)
    maker = generator(options)
    try:
        # Replace a few things to make this work better.
        # First, some scripts have names like __main__ and want to
        # peek at sys.argv; arguments for us will not be correct
        # for them, so we replace argv. Likewise, they may want to
        # exit, and we don't want them to do that.
        old_argv = sys.argv
        sys.argv = ['program', '--help']

        old_exit = sys.exit
        def exit(_arg):
            pass
        sys.exit = exit
        with maker:
            maker.retrieve()
        return maker
    finally:
        sys.argv = old_argv
        sys.exit = old_exit


if __name__ == '__main__':
    import logging
    logging.basicConfig()
    main()
    sys.exit(0)
