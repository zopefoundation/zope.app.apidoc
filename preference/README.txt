================
User Preferences
================

Implementing user preferences is usually a painful task, since it requires a
lot of custom coding and constantly changing preferences makes it hard to
maintain the data and UI. The `preference` package

  >>> from zope.app.apidoc.preference import preference

eases this pain by providing a generic user preferences framework that uses
schemas to categorize and describe the preferences.


Preferences Groups
------------------

Preferences are grouped in preference groups and the preferences inside a
group a spcified via the preferences group schema:

  >>> import zope.interface
  >>> import zope.schema
  >>> class IZMIUserSettings(zope.interface.Interface):
  ...     """Basic User Preferences"""
  ...
  ...     email = zope.schema.TextLine(
  ...         title=u"E-mail Address",
  ...         description=u"E-mail Address used to send notifications")
  ...
  ...     skin = zope.schema.Choice(
  ...         title=u"Skin",
  ...         description=u"The skin that should be used for the ZMI.",
  ...         values=['Rotterdam', 'ZopeTop', 'Basic'],
  ...         default='Rotterdam')
  ...
  ...     showZopeLogo = zope.schema.Bool(
  ...         title=u"Show Zope Logo",
  ...         description=u"Specifies whether Zope logo should be displayed "
  ...                     u"at the top of the screen.",
  ...         default=True)

Now we can instantiate the preference group. Each preference group must have a
name by which it can be accessed and has an optional title field for UI
purposes:

  >>> settings = preference.PreferencesGroup(
  ...     name="ZMISettings",
  ...     schema=IZMIUserSettings,
  ...     title=u"ZMI User Settings")

Note that the preferences group provides the interface it is representing:

  >>> IZMIUserSettings.providedBy(settings)
  True

and the name, schema and title of the group are directly available:

  >>> settings.name
  'ZMISettings'
  >>> settings.schema
  <InterfaceClass __builtin__.IZMIUserSettings>
  >>> settings.title
  u'ZMI User Settings'

So let's ask the group for the skin setting:

  >>> settings.skin #doctest:+ELLIPSIS
  Traceback (most recent call last):
  ...
  ComponentLookupError: 
  (<InterfaceClass ...interfaces.IPrincipalAnnotationUtility>, '')

So why did the lookup fail? Because we have not specified a principal yet, for
which we want to lookup the preferences. To do that, we have to create a new
interaction:

  >>> class Principal:
  ...     def __init__(self, id):
  ...         self.id = id
  >>> principal = Principal('zope.user')

  >>> class Participation:
  ...     interaction = None
  ...     def __init__(self, principal):
  ...         self.principal = principal

  >>> participation = Participation(principal)

  >>> import zope.security.management
  >>> zope.security.management.newInteraction(participation)

We also need a principal annotations utility, in which we store the settings:

  >>> from zope.app.principalannotation.interfaces import \
  ...         IPrincipalAnnotationUtility
  >>> class PrincipalAnnotations(dict):
  ...     zope.interface.implements(IPrincipalAnnotationUtility)
  ...
  ...     def getAnnotations(self, principal):
  ...         return self.setdefault(principal, {})

  >>> annotations = PrincipalAnnotations()

  >>> from zope.app.testing import ztapi
  >>> ztapi.provideUtility(IPrincipalAnnotationUtility, annotations)

Let's now try to access the settings again:

  >>> settings.skin
  'Rotterdam'

which is the default value, since we have not set it yet. We can now reassign
the value:

  >>> settings.skin = 'Basic'
  >>> settings.skin
  'Basic'

However, you cannot just enter any value, since it is validated before the
assignment:

  >>> settings.skin = 'MySkin'
  Traceback (most recent call last):
  ...
  ConstraintNotSatisfied: MySkin  


User Preferences
----------------

The various preferences groups are collectively available via the user
preferences object:

  >>> prefs = preference.UserPreferences()

Using this objcet, you can access a list of all available groups

  >>> prefs.items()
  []

But why did our new ZMI user settings group not appear? This is because we
have to register it first as a preferences group:

  >>> from zope.app.apidoc.preference.interfaces import IPreferencesGroup
  >>> ztapi.provideUtility(IPreferencesGroup, settings, settings.name)

Note that the name of the utility and the name saved in the group must be the
same. Now let's try again:

  >>> prefs.items() #doctest:+ELLIPSIS
  [(u'ZMISettings', 
    <zope.app.apidoc.preference.preference.PreferencesGroup object at ...>)]

You can also just access one group at a time:

  >>> prefs['ZMISettings'] #doctest:+ELLIPSIS
  <zope.app.apidoc.preference.preference.PreferencesGroup object at ...>

The entire `IReadContainer` interface is available.


Traversal
---------

Okay, so all these objects are nice, but they do not make it any easier to
access the preferences in page templates. Thus, a special traversal namespace
has been created that makes it very simple to access the preferences via a
traversal path. But before we can use the path expressions, we have to
register all necessary traversal components and the special `preferences`
namespace:

  >>> from zope.app.testing import setup
  >>> setup.setUpTraversal()

  >>> import zope.app.traversing.interfaces
  >>> ztapi.provideAdapter(None,
  ...                      zope.app.traversing.interfaces.ITraversable,
  ...                      preference.preferencesNamespace,
  ...                      'preferences')

We can now access the preferences as follows:

  >>> from zope.app import zapi

  >>> zapi.traverse(None, '++preferences++ZMISettings/skin')
  'Basic'
  >>> zapi.traverse(None, '++preferences++/ZMISettings/skin')
  'Basic'


Security
--------

You might already wonder under which permissions the preferences are
available. They are actually available publically (`CheckerPublic`), but that
is not a problem, since the available values are looked up specifically for
the current user. And why should a user not have full access to his/her
preferences? 

Let's create a checker using the function that the security machinery is
actually using:

  >>> checker = preference.PreferencesGroupChecker(settings)
  >>> checker.permission_id('skin')
  Global(CheckerPublic,zope.security.checker)
  >>> checker.setattr_permission_id('skin')
  Global(CheckerPublic,zope.security.checker)

The name, title and schema are publically available for access, but are not
available for mutation at all:

  >>> checker.permission_id('name')
  Global(CheckerPublic,zope.security.checker)
  >>> checker.setattr_permission_id('name') is None
  True


The only way security could be compromised is when one could override the
annotations property. However, this property is not available for public
consumption at all, including read access:

  >>> checker.permission_id('annotation') is None
  True
  >>> checker.setattr_permission_id('annotation') is None
  True
