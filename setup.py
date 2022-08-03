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
# This package is developed by the Zope Toolkit project, documented here:
# http://docs.zope.org/zopetoolkit
# When developing and releasing this package, please follow the documented
# Zope Toolkit policies as described by this documentation.
##############################################################################
"""Setup for zope.app.apidoc package

"""
import os

from setuptools import find_packages
from setuptools import setup


def read(*rnames):
    with open(os.path.join(os.path.dirname(__file__), *rnames)) as f:
        return f.read()


tests_require = [
    'zope.app.authentication >= 4.0.0',
    'zope.app.folder >= 4.0.0',
    'zope.app.http >= 4.0.1',
    'zope.app.principalannotation >= 4.0.0',
    'zope.app.rotterdam >= 4.0.1',
    'zope.app.wsgi >= 4.1.0',
    'zope.applicationcontrol >= 4.0.0',

    'zope.browserpage >= 4.1.0',
    'zope.login',
    'zope.principalannotation',
    'zope.securitypolicy',
    'zope.testing',
    'zope.testrunner',

    # If we wanted to depend on lxml, it can parse the results quite
    # a bit faster.

    # Things we don't use or configure, but which are
    # picked up indirectly by other packages and
    # need to be loaded to avoid errors running the
    # full static export.
    'zope.app.component[test]',
    'zope.app.form[test]',  # zc.sourcefactory
    'zope.app.schema[test]',
]

static_requires = tests_require

setup(
    name='zope.app.apidoc',
    version='4.3.1.dev0',
    author='Zope Corporation and Contributors',
    author_email='zope-dev@zope.org',
    description='API Documentation and Component Inspection for Zope 3',
    long_description=(
        read('README.rst')
        + '\n\n' +
        read('CHANGES.rst')
    ),
    license="ZPL 2.1",
    keywords="zope3 api documentation",
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: Zope Public License',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: Implementation :: CPython',
        'Programming Language :: Python :: Implementation :: PyPy',
        'Natural Language :: English',
        'Operating System :: OS Independent',
        'Topic :: Internet :: WWW/HTTP',
        'Framework :: Zope :: 3',
    ],
    url='http://github.com/zopefoundation/zope.app.apidoc',
    packages=find_packages('src'),
    include_package_data=True,
    package_dir={'': 'src'},
    namespace_packages=['zope', 'zope.app'],
    install_requires=[
        'persistent',
        'ZODB',
        'setuptools',
        'zope.annotation',
        'zope.app.appsetup >= 4.0.0',
        'zope.app.basicskin >= 4.0.0',
        'zope.app.exception >= 4.0.0',
        'zope.app.onlinehelp >= 4.0.1',
        'zope.app.preference >= 4.0.0',
        'zope.app.publisher >= 4.0.0',
        'zope.app.renderer >= 4.1.0',
        'zope.app.tree >= 4.0.0',
        'zope.cachedescriptors',
        'zope.component>=3.8.0',
        'zope.configuration',
        'zope.container',
        'zope.deprecation',
        'zope.hookable',
        'zope.i18n',
        'zope.interface',
        'zope.location >= 4.0.3',
        'zope.proxy',
        'zope.publisher >= 4.3.1',
        'zope.schema',
        'zope.security >= 4.1.1',
        'zope.site',
        'zope.testbrowser',
        'zope.testing',
        'zope.traversing >= 4.1.0',
    ],
    extras_require={
        'test': tests_require,
        'static': static_requires,
        'docs': [
            'repoze.sphinx.autointerface',
            'sphinx',
            'sphinx_rtd_theme',
            'sphinxcontrib-programoutput >= 0.11',
        ]
    },
    entry_points="""
        [console_scripts]
        static-apidoc = zope.app.apidoc.static:main
    """,
    zip_safe=False,
)
