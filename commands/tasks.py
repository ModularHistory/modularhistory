"""See Invoke's documentation: http://docs.pyinvoke.org/en/stable/."""

import os
from os.path import join
from typing import TYPE_CHECKING, Optional

import django
from decouple import config

from commands.command import command
from core.constants.environments import Environments

if TYPE_CHECKING:
    from invoke.context import Context

django.setup()

from django.conf import settings  # noqa: E402

GITHUB_CREDENTIALS_FILE = join(settings.BASE_DIR, '.github/.credentials')


@command
def build(  # noqa: S107
    context: 'Context',
    github_actor: str = '',
    access_token: str = '',
    sha: str = 'latest',
    push: bool = False,
    # default environment is delegated to ARG statement in Dockerfile
    environment: Optional[str] = None,
):
    """Build the Docker images used by ModularHistory."""
    if not access_token:
        access_token = config('GHCR_PASSWORD', default=None)
    if not all([github_actor, access_token, sha]):
        if os.path.exists(GITHUB_CREDENTIALS_FILE):
            print('Reading credentials...')
            with open(GITHUB_CREDENTIALS_FILE, 'r') as personal_access_token:
                signature = personal_access_token.read()
                github_actor, access_token = signature.split(':')
        else:
            raise ValueError(
                'Missing one or more required args: github_actor, access_token, sha.'
            )
    if push and environment != Environments.PROD:
        raise ValueError(f'Cannot push image built for {environment} environment.')
    print('Logging in to GitHub container registry...')
    context.run(
        f'echo {access_token} | docker login ghcr.io -u {github_actor} --password-stdin'
    )
    for image_name in ('django', 'next'):
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
def debug(context: 'Context'):
    """Print a message for debugging purposes."""
    context.run('echo "Success."')


@command
def generate_artifacts(context: 'Context'):
    """Generate artifacts."""
    from django.db.models import Count

    # Note: wordcloud is a dev-only dependency.
    from wordcloud import WordCloud

    from apps.topics.models.topic import Topic

    print('Building topics.txt...')
    ordered_topics = (
        Topic.objects.prefetch_related('topic_relations')
        .annotate(num_quotes=Count('topic_relations'))
        .order_by('-num_quotes')
    )
    text = '\n'.join([topic.name for topic in ordered_topics])
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
    word_cloud.to_file(join(settings.STATIC_ROOT, '_topic_cloud.png'))
    print('Done.')
