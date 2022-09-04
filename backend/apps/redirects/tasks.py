import logging
import os

from celery import Task
from django.conf import settings

from core.celery import app


@app.task(bind=True)
def write_map(self: Task, dry: bool = False):
    """Write a redirects.map file usable by Nginx."""
    # Avoid circular import, as this task is imported in models.py.
    from apps.redirects.models import Redirect

    redirects_map_path = os.path.join(settings.VOLUMES_DIR, 'redirects', 'redirects.map')
    redirects_map_lines = []
    redirect: Redirect
    for redirect in Redirect.objects.filter(site_id=settings.SITE_ID):
        redirects_map_lines.append(f'{redirect.old_path} {redirect.new_path};')
    redirects_map_content = '\n'.join(redirects_map_lines) + '\n'
    if dry:
        print(redirects_map_content)
    else:
        if os.path.exists(redirects_map_path):
            with open(redirects_map_path, 'r') as redirects_map:
                extant_redirects_map_content = redirects_map.read()
                if redirects_map_content == extant_redirects_map_content:
                    logging.info('Redirects map content has not changed.')
                    return
        with open(redirects_map_path, 'w') as redirects_map:
            redirects_map.write(redirects_map_content)
