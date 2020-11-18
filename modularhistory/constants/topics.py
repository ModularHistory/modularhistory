import os

from django.conf import settings

with open(os.path.join(settings.BASE_DIR, 'topics/topics.txt')) as artifact:
    TOPICS = artifact.readlines()
