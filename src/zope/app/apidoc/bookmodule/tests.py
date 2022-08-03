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
"""Tests for the Book Documentation Module

"""
import doctest
import unittest

from zope.app.apidoc.tests import standard_checker
from zope.app.apidoc.tests import standard_option_flags


def test_suite():
    return unittest.TestSuite((
        doctest.DocTestSuite(
            'zope.app.apidoc.bookmodule.browser',
            checker=standard_checker(),
            optionflags=standard_option_flags),
    ))
