def automoderate(instance, user):
    """
    Auto moderates given model instance on user. Returns moderation status:
    0 - Rejected
    1 - Approved
    """
    status = instance.moderation.automoderate(user)
    return status


def import_moderator(app):
    """
    Import moderator module and register all models it contains with moderation
    """
    import imp
    from importlib import import_module

    try:
        app_path = import_module(app).__path__
    except AttributeError:
        return None

    try:
        imp.find_module('moderator', app_path)
    except ImportError:
        return None

    module = import_module('%s.moderator' % app)

    return module


def auto_discover():
    """
    Auto register all apps that have module moderator with moderation
    """
    from django.conf import settings

    for app in [app for app in settings.INSTALLED_APPS if app != 'moderation']:
        import_moderator(app)
