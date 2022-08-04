##############################################################################
#
# Copyright (c) 2001, 2002 Zope Foundation and Contributors.
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
"""Meta-Configuration Handlers for "apidoc:bookchapter" directive.

"""
__docformat__ = 'restructuredtext'
import os.path

from zope.app.onlinehelp.onlinehelptopic import RESTOnlineHelpTopic

import zope.app.apidoc.bookmodule
from zope.app.apidoc.bookmodule.book import book


EMPTYPATH = os.path.join(
    os.path.dirname(zope.app.apidoc.bookmodule.__file__),
    'empty.txt')


def bookchapter(_context, id, title, doc_path=EMPTYPATH,
                parent="", resources=None):
    """Register a book chapter"""

    _context.action(
        discriminator=('apidoc:bookchapter', parent, id),
        callable=book.registerHelpTopic,
        args=(parent, id, title, doc_path),
        kw={'resources': resources, 'class_': RESTOnlineHelpTopic},
        order=999999)
