from .settings import IS_GCP

# If not in Google Cloud, initialize Celery.
if not IS_GCP:
    # This will make sure the app is always imported when Django starts,
    # so that shared_task will use this app.
    from .celery import app as celery_app
    __all__ = ('celery_app',)
