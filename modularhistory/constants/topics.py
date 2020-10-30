import os
from modularhistory import settings

with open(os.path.join(settings.BASE_DIR, 'topics/topics.txt')) as artifact:
    TOPICS = artifact.readlines()
