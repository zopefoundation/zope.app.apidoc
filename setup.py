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

from setuptools import setup, find_packages

setup(name = 'zope.app.apidoc',
      version = '3.4.0a1',
      url = 'http://svn.zope.org/zope.app.apidoc',
      license = 'ZPL 2.1',
      description = 'Zope apidoc',
      author = 'Zope Corporation and Contributors',
      author_email = 'zope3-dev@zope.org',
      long_description = "This Zope 3 package provides fully dynamic"
                         "API documentation of Zope 3 and registered"
                         "add-on components.",

      packages = find_packages('src'),
      package_dir = {'': 'src'},

      namespace_packages = ['zope', 'zope.app'],
      tests_require = ['zope.testing'],
      install_requires = ['setuptools',
                          'zope.annotation',
                          'zope.app.appsetup',
                          'zope.app.basicskin',
                          'zope.app.component',
                          'zope.app.container',
                          'zope.app.onlinehelp',
                          'zope.app.preference',
                          'zope.app.publisher',
                          'zope.app.renderer',
                          'zope.app.skins',
                          'zope.app.testing',
                          'zope.app.tree',
                          'zope.cachedescriptors',
                          'zope.component',
                          'zope.configuration',
                          'zope.deprecation',
                          'zope.i18n',
                          'zope.interface',
                          'zope.location',
                          'zope.proxy',
                          'zope.publisher',
                          'zope.schema',
                          'zope.security',
                          'zope.testbrowser',
                          'zope.testing',
                          'zope.traversing',
                          ],
      extras_require = dict(test=['zope.app.testing',
                                  'zope.app.securitypolicy',
                                  'zope.app.zcmlfiles'],
                            static=['mechanize'],
                            ),
      include_package_data = True,

      zip_safe = False,
      )
