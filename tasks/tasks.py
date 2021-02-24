"""See Invoke's documentation: http://docs.pyinvoke.org/en/stable/."""

import os
from os.path import join
from typing import Optional

import django
from decouple import config

from modularhistory.constants.environments import Environments
from modularhistory.utils import commands

from .command import command

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'modularhistory.settings')
django.setup()

from django.conf import settings  # noqa: E402

GITHUB_API_BASE_URL = 'https://api.github.com'
OWNER = 'modularhistory'
REPO = 'modularhistory'
GITHUB_ACTIONS_BASE_URL = f'{GITHUB_API_BASE_URL}/repos/{OWNER}/{REPO}/actions'
GITHUB_CREDENTIALS_FILE = '.github/.credentials'


@command
def build(
    context,
    github_actor: str,
    access_token: str,
    sha: str,
    push: bool = False,
    # default environment is delegated to ARG statement in Dockerfile
    environment: Optional[str] = None,
):
    """Build the Docker images used by ModularHistory."""
    if not access_token:
        access_token = config('CR_PAT', default=None)
    if not all([github_actor, access_token, sha]):
        raise ValueError(
            'Missing one or more required args: github_actor, access_token, sha.'
        )
    if push and environment != Environments.PROD:
        raise ValueError(f'Cannot push image built for {environment} environment.')
    print('Logging in to GitHub container registry...')
    context.run(
        f'echo {access_token} | docker login ghcr.io -u {github_actor} --password-stdin'
    )
    for image_name in ('django', 'react'):
        image = f'ghcr.io/modularhistory/{image_name}'
        print(f'Pulling {image}:latest...')
        context.run(f'docker pull {image}:latest', warn=True)
        print(f'Building {image}:{sha}...')
        extant = context.run(f'docker inspect {image}:latest', warn=True).exited == 0
        build_command = (
            f'docker build . -f Dockerfile.{image_name} -t {image}:{sha} '
            f'--build-arg ENVIRONMENT={environment}'
        )
        if extant:
            build_command = f'{build_command} --cache-from {image}:latest'
        print(build_command)
        context.run(build_command)
        context.run(f'docker tag {image}:{sha} {image}:latest')
        context.run(f'docker run -d {image}:{sha}')
        if push:
            print(f'Pushing new image ({image}:{sha}) to the container registry..."')
            context.run(f'docker push {image}:{sha} && docker push {image}:latest')


@command
def generate_artifacts(context):
    """Generate artifacts."""
    from django.db.models import Count
    from wordcloud import WordCloud

    from apps.topics.models import Topic

    print('Building topics.txt...')
    ordered_topics = (
        Topic.objects.prefetch_related('topic_relations')
        .annotate(num_quotes=Count('topic_relations'))
        .order_by('-num_quotes')
    )
    text = '\n'.join([topic.key for topic in ordered_topics])
    with open(join(settings.BASE_DIR, 'topics/topics.txt'), mode='w+') as artifact:
        artifact.write(text)

    print('Building topic_cloud.png...')
    # https://github.com/amueller/word_cloud
    word_cloud = WordCloud(
        background_color=None,
        mode='RGBA',
        width=1200,
        height=700,
        min_font_size=6,
        collocations=False,
        normalize_plurals=False,
        regexp=r'\w[\w\' ]+',
    ).generate(text)
    word_cloud.to_file(join(settings.BASE_DIR, 'static', '_topic_cloud.png'))
    print('Done.')
