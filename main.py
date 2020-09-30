"""Google Cloud App Engine entrypoint."""

from modularhistory.wsgi import application

# App Engine by default looks for a main.py file at the root of the app
# directory with a WSGI-compatible obj called app.
# This file imports the WSGI-compatible obj of the Django app,
# application from history/wsgi.py and renames it app so it is
# discoverable by App Engine without additional configuration.
# Alternatively, you can add a custom entrypoint field in your app.yaml:
# entrypoint: gunicorn -b :$PORT history.wsgi
app = application
