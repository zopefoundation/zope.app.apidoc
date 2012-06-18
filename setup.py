##############################################################################
#
# Copyright (c) 2006 Zope Foundation and Contributors.
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

def read(*rnames):
    return open(os.path.join(os.path.dirname(__file__), *rnames)).read()

setup(
    name = 'zope.app.apidoc',
    version = '3.4.4dev',
    author = 'Zope Corporation and Contributors',
    author_email = 'zope3-dev@zope.org',
    description = 'API Documentation and Component Inspection for Zope 3',
    long_description=(
        read('README.txt')
        + '\n\n' +
        'Detailed Documentation\n' +
        '**********************\n\n'
        + '\n\n' +
        read('src', 'zope', 'app', 'apidoc', 'README.txt')
        + '\n\n' +
        read('src', 'zope', 'app', 'apidoc', 'component.txt')
        + '\n\n' +
        read('src', 'zope', 'app', 'apidoc', 'interface.txt')
        + '\n\n' +
        read('src', 'zope', 'app', 'apidoc', 'presentation.txt')
        + '\n\n' +
        read('src', 'zope', 'app', 'apidoc', 'utilities.txt')
        + '\n\n' +
        read('src', 'zope', 'app', 'apidoc', 'classregistry.txt')
        + '\n\n' +
        read('CHANGES.txt')
        ),
    license = "ZPL 2.1",
    keywords = "zope3 api documentation",
    classifiers = [
        'Development Status :: 5 - Production/Stable',
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: Zope Public License',
        'Programming Language :: Python',
        'Natural Language :: English',
        'Operating System :: OS Independent',
        'Topic :: Internet :: WWW/HTTP',
        'Framework :: Zope3'],
    url = 'http://cheeseshop.python.org/pypi/zope.app.apidoc',
    packages = find_packages('src'),
    include_package_data = True,
    package_dir = {'':'src'},
    namespace_packages = ['zope', 'zope.app'],
    tests_require = ['zope.testing'],
    install_requires = [
        'setuptools',
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
      extras_require = dict(
          test=['zope.app.testing',
                'zope.app.securitypolicy',
                'zope.app.zcmlfiles',
                'zope.securitypolicy'],
          static=['mechanize'],
          ),
      entry_points = """
        [console_scripts]
        static-apidoc = zope.app.apidoc.static:main
        """,
      zip_safe = False,
      )
