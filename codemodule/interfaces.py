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
"""Interfaces for code browser

$Id$
"""
__docformat__ = "reStructuredText"
from zope.interface import Interface
from zope.schema import Field, BytesLine, Text

from zope.app.container.interfaces import IContainer
from zope.app.container.interfaces import IReadContainer
from zope.app.i18n import ZopeMessageIDFactory as _


class IModuleDocumentation(IReadContainer):
    """Representation of a Python module for documentation.

    The items of the container are sub-modules and classes.
    """
    def getDocString():
        """Return the doc string of the module."""

    def getFileName():
        """Return the file name of the module."""

    def getPath():
        """Return the Python path of the module."""


class IClassDocumentation(Interface):
    """Representation of a class or type for documentation."""

    def getDocString():
        """Return the doc string of the class."""

    def getPath():
        """Return the Python path of the class."""

    def getBases():
        """Return the base classes of the class."""

    def getKnownSubclasses():
        """Return the known subclasses classes of the class."""

    def getInterfaces():
        """Return the interfaces the class implements."""

    def getAttributes():
        """Return a list of 3-tuple attribute information.

        The first entry of the 3-tuple is the name of the attribute, the
        second is the attribute object itself. The third entry is the
        interface in which the attribute is defined.

        Note that only public attributes are returned, meaning only attributes
        that do not start with an '_'-character.
        """

    def getMethods():
        """Return a list of 3-tuple method information.

        The first entry of the 3-tuple is the name of the method, the
        second is the method object itself. The third entry is the
        interface in which the method is defined.

        Note that only public methods are returned, meaning only methods
        that do not start with an '_'-character.
        """

    def getSecurityChecker():
        """Return the security checker for this class.

        Since 99% of the time we are dealing with name-based security
        checkers, we can look up the get/set permission required for a
        particular class attribute/method.
        """


class IFunctionDocumentation(Interface):
    """Representation of a function for documentation."""

    def getDocString():
        """Return the doc string of the function."""

    def getPath():
        """Return the Python path of the function."""

    def getSignature():
        """Return the signature of the function as a string."""

    def getAttributes():
        """Return a list of 2-tuple attribute information.

        The first entry of the 2-tuple is the name of the attribute, the
        second is the attribute object itself.
        """


class IElement(IContainer):
    """Represents an XML Element in the ZCML Configuration File

    The names of the container items is simply their index (as string).
    """

    domElement = Field(
        title=_("Mini-DOM Element"),
        description=_("Mini-DOM element representing this configuration "
                      "element."),
        required=True)

    def toXML():
        """Returns a string completely representing this DOM Element.
        
        The returned XML should be well formatted, including all correct
        indentations and lines not being long than 80 characters, if possible.
        """

    def getElementType():
        """Return the type of the DOM element.
        
        Possible values are:

        - ELEMENT_NODE (1): An XML tag. If an element is of this type it is a
          standard ZCML directive or sub-directive.

        - COMMENT_NODE (8): An XML comment. Comments are used to explain
          features of the ZCML directives and are thus supported by the editor.

        - TEXT_NODE (3): A simple text node. These are commonly ignored by te
          configuration editor, since they are arbitrary and ZCML does not make
          use of text nodes ever. Thus, an element having this type would be
          considered a bug.
        """

    def isFirstChild():
        """Determine whether this element is the first child in its parent."""

    def isLastChild():
        """Determine whether this element is the last child in its parent."""

    def validate():
        """Validate the element's data.

        If the validation is successful, `None` should be returned; otherwise
        return a `ValidationError` or a list of validation errors.

        While a DOM element always represents a valid XML expression, this might
        not be true for ZCML, since it is just a subset of XML.
        """


class IComment(IElement):
    """A special element representing a comment in the configuration."""

    value = Text(
        title=_("Comment"),
        description=_("This is the actual comment text. It is automatically "
                      "extracted from the DOM element."),
        required=True)


class IDirective(IElement):
    """

    The element will also expose the attributes of the XML element as attributes
    of this class.
    """
    config = Field()

    schema = Field()

    def getFullTagName():
        """ """

    def getAttribute(name):
        """ """

    def getAttributeMap():
        """ """

    def removeAttribute(name):
        """ """

    def getAvailableSubdirectives():
        """ """
        

class IConfiguration(IDirective):
    """ZCML Configuration Object

    This is the main object that will manage the configuration of one particular
    ZCML configuration file.
    """

    filename = BytesLine(
        title=_('Configuration Filename'),
        description=_('Path to the configuration file'),
        required=True)

    package = BytesLine(
        title=_('Configuration Package'),
        description=_(
        '''Specifies the package from which the configuration file will be
        executed. If you do not specify the package, then the configuration
        cannot be fully validated and improper ZCML files might be written.'''),
        required=False)

    def parse():
        """Parse the ZCML located in the specified file.

        If the file does not exist, a configuration will be initialized.
        """

    def getSchema(namespaceURI, tagName):
        """Given the namespace and the tag name, lookup the directive's
        schema.

        If no schema is found, `None` is returned.
        """

    def getNamespacePrefix(namespaceURI):
        """ """

    def getNamespaceURI(prefix):
        """ """

    def getResolver():
        """ """
