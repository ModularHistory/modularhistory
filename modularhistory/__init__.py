"""__init__.py for base ModularHistory application."""

# Make sure the app is always imported when Django starts,
# so that shared_task will use this app.
from .tasks import app as celery_app
