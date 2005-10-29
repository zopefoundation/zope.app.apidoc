##############################################################################
#
# Copyright (c) 2005 Zope Corporation and Contributors.
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

$Id$
"""
__docformat__ = "reStructuredText"

import base64
import os
import sys
import time
import urllib2
import HTMLParser

import zope.testbrowser
import mechanize

from zope.app.testing import functional

# Setup the user feedback detail level.
VERBOSITY = 2

VERBOSITY_MAP = {1: 'ERROR', 2: 'WARNING', 3: 'INFO'}

USE_PUBLISHER = True

URL = 'http://localhost:8080/'

START_PAGE = '++apidoc++/Type/@@staticmenu.html'

BASE_DIR = 'apidoc'

# A mapping of HTML elements that can contain links to the attribute that
# actually contains the link
urltags = {
    "a": "href",
    "area": "href",
    "frame": "src",
    "iframe": "src",
    "link": "href",
    "img": "src",
    "script": "src",
}

# Additional URLs that are not referenced in the HTML, but are still used, via
# Javascript, for example.
additionalURLs = [
    '@@/varrow.png',
    '@@/harrow.png',
    '@@/tree_images/minus.png',
    '@@/tree_images/plus.png',
    '@@/tree_images/minus_vline.png',
    '@@/tree_images/plus_vline.png',
]

def getMaxWidth():
    try:
        import curses
    except ImportError:
        pass
    else:
        try:
            curses.setupterm()
            cols = curses.tigetnum('cols')
            if cols > 0:
                return cols
        except curses.error:
            pass
    return 80

def cleanURL(url):
    """Clean a URL from parameters."""
    if '?' in url:
        url = url.split('?')[0]
    if '#' in url:
        url = url.split('#')[0]
    return url

def completeURL(url):
    """Add file to URL, if not provided."""
    if url.endswith('/'):
        url += 'index.html'
    if '.' not in url.split('/')[-1]:
        url += '/index.html'
    filename = url.split('/')[-1]
    if filename.startswith('@@'):
        url = url.replace(filename, filename[2:])
    return url


class Link(object):
    """A link in the page."""

    def __init__(self, mechLink, referenceURL=None):
        self.referenceURL = referenceURL
        self.originalURL = mechLink.url
        self.callableURL = mechLink.absolute_url
        self.url = completeURL(cleanURL(mechLink.url))
        self.absoluteURL = completeURL(cleanURL(mechLink.absolute_url))

    def isLocalURL(self):
        """Determine whether the passed in URL is local and accessible."""
        # Javascript function call
        if self.url.startswith('javascript:'):
            return False
        # Mail Link
        if self.url.startswith('mailto:'):
            return False
        # External Link
        if self.url.startswith('http://') and not self.url.startswith(URL):
            return False
        return True

    def isApidocLink(self):
        # Make sure that only apidoc links are loaded
        if self.absoluteURL.startswith(URL+'++apidoc++/'):
            return True
        if self.absoluteURL.startswith(URL+'@@/'):
            return True
        return False


class OnlineBrowser(mechanize.Browser, object):

    def setUserAndPassword(self, user, pw):
        """Specify the username and password to use for the retrieval."""
        hash = base64.encodestring(user+':'+pw).strip()
        self.addheaders.append(('Authorization', 'Basic '+hash))

    @property
    def contents(self):
        """Get the content of the returned data"""
        response = self.response()
        old_location = response.tell()
        response.seek(0)
        contents = response.read()
        response.seek(old_location)
        return contents


class PublisherBrowser(zope.testbrowser.testing.PublisherMechanizeBrowser,
                       object):

    def __init__(self, *args, **kw):
        functional.FunctionalTestSetup()
        super(PublisherBrowser, self).__init__(*args, **kw)

    def setUserAndPassword(self, user, pw):
        """Specify the username and password to use for the retrieval."""
        self.addheaders.append(('Authorization', 'Basic %s:%s' %(user, pw)))

    @property
    def contents(self):
        """Get the content of the returned data"""
        response = self.response()
        old_location = response.tell()
        response.seek(0)
        # Remove HTTP Headers
        for line in iter(lambda: response.readline().strip(), ''):
            pass
        contents = response.read()
        response.seek(old_location)
        return contents


class StaticAPIDocGenerator(object):
    """Static API doc Maker"""

    def __init__(self):
        self.linkQueue = []
        for url in  additionalURLs + [START_PAGE]:
            link = Link(mechanize.Link(URL, url, '', '', ()))
            self.linkQueue.append(link)
        self.rootDir = os.path.join(os.path.dirname(__file__), BASE_DIR)
        self.maxWidth = getMaxWidth()-13
        self.needNewLine = False

    def start(self):
        """Start the retrieval of the apidoc."""
        t0 = time.time()

        self.visited = []
        self.counter = 0

        if not os.path.exists(self.rootDir):
            os.mkdir(self.rootDir)

        if USE_PUBLISHER:
            self.browser = PublisherBrowser()
        else:
            self.browser = OnlineBrowser()

        self.browser.setUserAndPassword('mgr', 'mgrpw')
        self.browser.urltags = urltags

        # Work through all links until there are no more to work on.
        self.sendMessage('Starting retrieval.')
        while self.linkQueue:
            link = self.linkQueue.pop()
            # Sometimes things are placed many times into the queue, for example
            # if the same link appears twice in a page. In those cases, we can
            # check at this point whether the URL has been already handled.
            if link.absoluteURL not in self.visited:
                self.showStatistics(link)
                self.processLink(link)

        t1 = time.time()

        self.sendMessage("Run time: %.3f sec real" % (t1-t0))

    def showStatistics(self, link):
        self.counter += 1
        if VERBOSITY >= 3:
            url = link.absoluteURL[-(self.maxWidth):]
            sys.stdout.write('\r' + ' '*(self.maxWidth+13))
            sys.stdout.write('\rLink %5d: %s' % (self.counter, url))
            sys.stdout.flush()
            self.needNewLine = True

    def sendMessage(self, msg, verbosity=4):
        if VERBOSITY >= verbosity:
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
        self.visited.append(url)

        # Retrieve the content
        try:
            self.browser.open(link.callableURL)
        except urllib2.HTTPError, error:
            # Something went wrong with retrieving the page.
            self.sendMessage(
                '%s (%i): %s' % (error.msg, error.code, link.callableURL), 2)
            self.sendMessage('+-> Reference: ' + link.referenceURL, 2)
            return
        except (urllib2.URLError, ValueError):
            # We had a bad URL running the publisher browser
            self.sendMessage('Bad URL: ' + link.callableURL, 2)
            self.sendMessage('+-> Reference: ' + link.referenceURL, 2)
            return

        # Make sure the directory exists and get a file path.
        relativeURL = url.replace(URL, '')
        dir = self.rootDir
        segments = relativeURL.split('/')
        filename = segments.pop()

        for segment in segments:
            dir = os.path.join(dir, segment)
            if not os.path.exists(dir):
                os.mkdir(dir)

        filepath = os.path.join(dir, filename)

        # Get the response content
        contents = self.browser.contents

        # Now retrieve all links
        if self.browser.viewing_html():

            try:
                links = self.browser.links()
            except HTMLParser.HTMLParseError:
                self.sendMessage('Failed to parse HTML: ' + url, 1)
                links = []

            links = [Link(mech_link, url) for mech_link in links]

            for link in links:
                # Make sure we do not handle unwanted links.
                if not (link.isLocalURL() and link.isApidocLink()):
                    continue

                # Add link to the queue
                if link.absoluteURL not in self.visited:
                    self.linkQueue.insert(0, link)

                # Rewrite URLs
                parts = ['..']*len(segments)
                parts.append(link.absoluteURL.replace(URL, ''))
                contents = contents.replace(link.originalURL, '/'.join(parts))

        # Write the data into the file
        file = open(filepath, 'w')
        file.write(contents)
        file.close()

        # Cleanup; this is very important, otherwise we are opening too many
        # files.
        self.browser.close()

def main():
    global BASE_DIR
    BASE_DIR = sys.argv[1]
    maker = StaticAPIDocGenerator()
    maker.start()
    sys.exit(0)
