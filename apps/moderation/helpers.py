def automoderate(instance, user):
    """
    Auto moderates given model instance on user. Returns moderation status:
    0 - Rejected
    1 - Approved
    """
    status = instance.moderation.automoderate(user)
    return status
