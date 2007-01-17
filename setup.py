##############################################################################
#
# Copyright (c) 2006 Zope Corporation and Contributors.
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
"""Setup for zope.app.apidoc package

$Id$
"""

import os

try:
    from setuptools import setup, Extension
except ImportError, e:
    from distutils.core import setup, Extension

setup(name='zope.app.apidoc',
      version='3.4-dev',
      url='http://svn.zope.org/zope.app.apidoc',
      license='ZPL 2.1',
      description='Zope apidoc',
      author='Zope Corporation and Contributors',
      author_email='zope3-dev@zope.org',
      long_description="This Zope 3 package provides fully dynamic"
                       "API documentation of Zope 3 and registered"
                       "add-on components.",

      packages=['zope', 'zope.app', 'zope.app.apidoc',
                'zope.app.apidoc.bookmodule',
                'zope.app.apidoc.browser',
                'zope.app.apidoc.codemodule',
                'zope.app.apidoc.codemodule.browser',
                'zope.app.apidoc.typemodule',
                'zope.app.apidoc.utilitymodule',
                'zope.app.apidoc.zcmlmodule'],
      package_dir = {'': 'src'},

      namespace_packages=['zope', 'zope.app'],
      tests_require = ['zope.testing'],
      install_requires=['zope.interface'],
      include_package_data = True,

      zip_safe = False,
      )
