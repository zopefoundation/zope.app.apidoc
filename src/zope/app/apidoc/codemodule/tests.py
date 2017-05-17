##############################################################################
#
# Copyright (c) 2004 Zope Foundation and Contributors.
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
"""Tests for the Code Documentation Module

"""

import unittest
import doctest

from zope.component import testing

from zope.app.apidoc.tests import standard_checker
from zope.app.apidoc.tests import standard_option_flags
from zope.app.apidoc.tests import LayerDocFileSuite
import zope.app.apidoc.codemodule


def test_suite():
    checker = standard_checker()

    return unittest.TestSuite((
        LayerDocFileSuite(
            'README.rst',
            zope.app.apidoc.codemodule),
        doctest.DocFileSuite(
            'directives.rst',
            setUp=testing.setUp,
            tearDown=testing.tearDown,
            checker=checker,
            optionflags=standard_option_flags),
    ))

if __name__ == '__main__':
    unittest.main(defaultTest="test_suite")
