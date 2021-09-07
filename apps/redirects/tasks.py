import os

from celery import Task
from django.conf import settings

from apps.redirects.models import Redirect
from core.celery import app


@app.task(bind=True)
def write_redirects_map(self: Task, dry: bool = False):
    """Write a redirects.map file usable by Nginx."""
    redirects_map_path = os.path.join(settings.VOLUMES_DIR, 'redirects', 'redirects.map')
    redirects_map_lines = []
    redirect: Redirect
    for redirect in Redirect.objects.all():
        redirects_map_lines.append(f'{redirect.old_path} {redirect.new_path}')
    redirects_map_content = '\n'.join(redirects_map_lines)
    if dry:
        print(redirects_map_content)
    else:
        with open(redirects_map_path, 'w') as redirects_map:
            redirects_map.write(redirects_map_content)
