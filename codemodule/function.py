##############################################################################
#
# Copyright (c) 2004 Zope Corporation and Contributors.
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
"""Function representation for code browser 

$Id: __init__.py 29143 2005-02-14 22:43:16Z srichter $
"""
__docformat__ = 'restructuredtext'
from zope.interface import implements
from zope.app.location.interfaces import ILocation

from zope.app.apidoc.utilities import getFunctionSignature
from interfaces import IFunctionDocumentation

class Function(object):
    """This class represents a function declared in the module.

    Setting up a function for documentation is easy. You only need to provide
    an object providing 'IModule' as a parent, the name and the function
    object itself::

      >>> import zope.app.apidoc
      >>> module = Module(None, 'apidoc', zope.app.apidoc)
      >>> func = Function(module, 'handleNamespace',
      ...                 zope.app.apidoc.handleNamespace)

    This class provides data about the function in an accessible format. The
    Python path, signature and doc string are easily retrieved using::

      >>> func.getPath()
      'zope.app.apidoc.handleNamespace'

      >>> func.getSignature()
      '(ob, name)'

      >>> func.getDocString()
      'Used to traverse to an API Documentation.'

    For a more detailed analysis, you can also retrieve the attributes of the
    function::

      >>> func.getAttributes()
      []
    """
    implements(ILocation, IFunctionDocumentation)

    def __init__(self, module, name, func):
        self.__parent__ = module
        self.__name__ = name
        self.__func = func

    def getPath(self):
        """See IFunctionDocumentation."""
        return self.__parent__.getPath() + '.' + self.__name__

    def getDocString(self):
        """See IFunctionDocumentation."""
        return self.__func.__doc__

    def getSignature(self):
        """See IFunctionDocumentation."""
        return getFunctionSignature(self.__func)

    def getAttributes(self):
        """See IClassDocumentation.

        Here a detailed example::

          >>> class ModuleStub(object):
          ...      def getPath(self): return ''

          >>> def foo(bar=1):
          ...     pass

          >>> func = Function(ModuleStub(), 'foo', foo)

          >>> attrs = func.getAttributes()
          >>> attrs.sort()
          >>> print attrs
          []

          >>> foo.bar = 'blah'
          >>> attrs = func.getAttributes()
          >>> attrs.sort()
          >>> print attrs
          [('bar', 'blah')]
        """
        return self.__func.__dict__.items()
