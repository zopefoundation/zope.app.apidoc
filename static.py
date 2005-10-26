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

import os
import sys
import time
import urllib2
import HTMLParser

import zope.testbrowser
import mechanize

from zope.app.testing import functional

# Setup the user feedback detail level.
VERBOSITY = 4

VERBOSITY_MAP = {1: 'ERROR', 2: 'WARNING', 3: 'INFO'}

USE_PUBLISHER = True

URL = 'http://localhost:8080/'

START_PAGE = '++apidoc++/static.html'

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
        url += '@@index.html'
    if '.' not in url.split('/')[-1]:
        url += '/@@index.html'
    return url

def isLocalURL(url):
    """Determine whether the passed in URL is local and accessible."""
    if url.startswith('javascript:'):
        return False
    if url.startswith('mailto:'):
        return False
    if url.startswith('http://') and not url.startswith(URL):
        return False
    return True


class StaticAPODoc(object):
    """Static API doc Maker"""

    def __init__(self):
        self.linkQueue = [mechanize.Link(URL, START_PAGE, '', '', ())]
        for url in additionalURLs:
            self.linkQueue.append(mechanize.Link(URL, url, '', '', ()))
        self.rootDir = os.path.join(os.path.dirname(__file__), BASE_DIR)
        self.maxWidth = getMaxWidth()-13

    def start(self):
        """Start the retrieval of the apidoc."""
        t0 = time.time()
        c0 = time.clock()

        self.visited = []
        self.counter = 0

        if not os.path.exists(self.rootDir):
            os.mkdir(self.rootDir)

        if USE_PUBLISHER:
            self.sendMessage('Setting up Zope 3.')
            functional.FunctionalTestSetup()
            self.browser = zope.testbrowser.testing.PublisherMechanizeBrowser()
            self.browser.addheaders.append(
                ('Authorization', 'Basic mgr:mgrpw'))
        else:
            self.browser = mechanize.Browser()
            self.browser.addheaders.append(
                ('Authorization', 'Basic Z2FuZGFsZjoxMjM='))

        self.browser.urltags = urltags

        # Work through all links until there are no more to work on.
        self.sendMessage('Starting retrieval.')
        while self.linkQueue:
            link = self.linkQueue.pop()
            # Sometimes things are placed many times into the queue, for example
            # if the same link appears twice in a page. In those cases, we can
            # check at this point whether the URL has been already handled.
            if link.absolute_url not in self.visited:
                self.showStatistics(link)
                self.processLink(link)

        t1 = time.time()
        c1 = time.clock()

        self.sendMessage(
            "Run time: %.3f sec real, %.3f sec CPU" %(t1-t0, c1-c0))

    def showStatistics(self, link):
        self.counter += 1
        if VERBOSITY >= 3:
            url = link.absolute_url[-(self.maxWidth):]
            sys.stdout.write('\r' + ' '*(self.maxWidth+13))
            sys.stdout.write('\rLink %5d: %s' % (self.counter, url))
            sys.stdout.flush()

    def sendMessage(self, msg, verbosity=4):
        if verbosity >= VERBOSITY:
            sys.stdout.write('\n')
            sys.stdout.write(VERBOSITY_MAP.get(verbosity, 'INFO')+': ')
            sys.stdout.write(msg)
            sys.stdout.write('\n')
            sys.stdout.flush()

    def processLink(self, link):
        """Process a link."""
        url = link.absolute_url

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

        # Whatever will happen, we have looked at the URL
        self.visited.append(url)

        # Retrieve the content
        try:
            self.browser.open(url)
        except urllib2.HTTPError:
            # TODO: Provide less misleading message; many different errors can
            #       happen here.
            self.sendMessage('Link not found: ' + link.absolute_url, 2)
            return
        except ValueError:
            # We had a bad URL running the publisher browser
            self.sendMessage('Bad URL: ' + link.absolute_url, 2)
            return

        response = self.browser.response()
        old_location = response.tell()
        response.seek(0)

        if USE_PUBLISHER:
            # Remove HTTP Headers
            for line in iter(lambda: response.readline().strip(), ''):
                pass

        contents = response.read()
        response.seek(old_location)

        # Now retrieve all links
        if self.browser.viewing_html():

            try:
                links = self.browser.links()
            except HTMLParser.HTMLParseError:
                self.sendMessage('Failed to parse HTML: ' + url, 1)
                links = []

            for link in links:
                # Make sure URLs have file extensions, but no parameters
                link.url = completeURL(cleanURL(link.url))
                link.absolute_url = completeURL(cleanURL(link.absolute_url))
                # Add link to the queue
                if link.absolute_url not in self.visited:
                    if isLocalURL(link.url):
                        self.linkQueue.insert(0, link)

                # Rewrite URLs
                if isLocalURL(link.url):
                    parts = ['..']*len(segments)
                    parts.append(link.absolute_url.replace(URL, ''))
                    contents = contents.replace(link.url, '/'.join(parts))

        # Write the data into the file
        file = open(filepath, 'w')
        file.write(contents)
        file.close()

        # Cleanup; this is very important, otherwise we are opening too many
        # files.
        self.browser.response().close() # bug fix
        self.browser.close()
        self.browser._history = [] # bug fix


def main():
    global BASE_DIR
    BASE_DIR = sys.argv[1]
    maker = StaticAPODoc()
    maker.start()
    sys.exit(0)
