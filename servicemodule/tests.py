##############################################################################
#
# Copyright (c) 2004 Zope Corporation and Contributors.
# All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.0 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
##############################################################################
"""Tests for the Service Documentation Module

$Id: tests.py,v 1.1 2004/02/19 20:46:41 philikon Exp $
"""
import unittest
from zope.testing.doctestunit import DocTestSuite
    
def test_suite():
    return unittest.TestSuite((
        DocTestSuite('zope.app.apidoc.servicemodule'),
        ))

if __name__ == '__main__':
    unittest.main()
