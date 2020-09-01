import os
import importlib.util

IS_GCP = bool(os.getenv('GAE_APPLICATION', None))

# If not in Google Cloud, initialize Celery.
if not IS_GCP:
    # This will make sure the app is always imported when Django starts,
    # so that shared_task will use this app.
    from .tasks import app as celery_app
    __all__ = ('celery_app',)

# TODO
# # https://www.ralphminderhoud.com/blog/django-mypy-check-runs/
# mypy_package = importlib.util.find_spec("mypy")
# if mypy_package:
#     from .checks import mypy
