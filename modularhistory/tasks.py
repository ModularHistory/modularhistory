from invoke.context import Context

CONTEXT = Context()


def dbbackup(context: Context = CONTEXT):
    """Create a database backup file."""
    context.run('invoke dbbackup')


def mediabackup(context: Context = CONTEXT):
    """Create a media backup file."""
    context.run('invoke mediabackup')
