"""
These "tasks" or commands can be invoked from the console via the "invoke" command.

For example:
``
invoke lint
invoke test
``

Note: Invoke must first be installed by running setup.sh or `poetry install`.

See Invoke's documentation: http://docs.pyinvoke.org/en/stable/.
"""

import os
from typing import Any, Callable, TypeVar

import django
from pympler import tracker
from modularhistory import settings
from modularhistory.constants.strings import NEGATIVE, SPACE
from modularhistory.linters import flake8 as lint_with_flake8
from modularhistory.linters import mypy as lint_with_mypy
from modularhistory.utils import commands
from modularhistory.utils.files import relativize
from monkeypatch import fix_annotations

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'modularhistory.settings')
django.setup()

if fix_annotations():
    import invoke

TaskFunction = TypeVar('TaskFunction', bound=Callable[..., Any])


def task(task_function: TaskFunction) -> TaskFunction:
    """Wrap invoke.task to enable type annotations."""
    task_function.__annotations__ = {}
    return invoke.task(task_function)


@task
def autoformat(context):
    """Safely run autoformatters against all Python files."""
    commands.autoformat(context)


@task
def commit(context):
    """Commit and (optionally) push code changes."""
    # Check that the branch is correct
    context.run('git branch')
    print('\nCurrent branch: ')
    branch = context.run('git branch --show-current').stdout
    if input('\nContinue? [Y/n] ') == NEGATIVE:
        return

    # Stage files, if needed
    context.run('git status')
    if input('\nStage all changed files? [Y/n] ') == NEGATIVE:
        while input('Do files need to be staged? [Y/n] ') != NEGATIVE:
            files_to_stage = input('Enter filenames and/or patterns: ')
            context.run(f'git add {files_to_stage}')
            context.run('echo "" && git status')
    else:
        context.run('git add .')

    # Commit the changes
    commit_msg = None
    while commit_msg is None:
        commit_msg_input = input('\nEnter a commit message (without double quotes): ')
        if commit_msg_input and '"' not in commit_msg_input:
            commit_msg = commit_msg_input
            break
    print(f'\n{commit_msg}\n')
    if input('Is this commit message correct? [Y/n] ') != NEGATIVE:
        context.run(f'git commit -m "{commit_msg}"')

    # Push the changes, if desired
    if input('\nPush changes to remote branch? [Y/n] ') == NEGATIVE:
        print(
            'To push your changes to the repository, use the following command: \n'
            'git push'
        )
    else:
        context.run('git push')
        diff_link = f'https://github.com/ModularHistory/modularhistory/compare/{branch}'
        print(f'\nCreate pull request / view diff: {diff_link}')


@task
def flake8(context, *args):
    """Run flake8 linter."""
    lint_with_flake8(interactive=True)


@task
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
    with open(
        os.path.join(settings.BASE_DIR, 'topics/topics.txt'), mode='w+'
    ) as artifact:
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
    word_cloud.to_file(os.path.join(settings.BASE_DIR, 'static', 'topic_cloud.png'))
    print('Done.')


@task
def mypy(context, *args):
    """Run mypy static type checker."""
    lint_with_mypy()


@task
def lint(context, *args):
    """Run linters."""
    # Run Flake8
    print('Running flake8...')
    lint_with_flake8(interactive=True)

    # Run MyPy
    print('Running mypy...')
    lint_with_mypy()


@task
def makemigrations(context, noninteractive: bool = False):
    """Safely create migrations."""
    commands.makemigrations(context, noninteractive=noninteractive)


@task
def migrate(context, *args, noninteractive: bool = False):
    """Safely run db migrations."""
    commands.migrate(context, *args, noninteractive=noninteractive)


@task
def nox(context, *args):
    """Run linters and tests in multiple environments using nox."""
    nox_cmd = SPACE.join(['nox', *args])
    context.run(nox_cmd)
    context.run('rm -r modularhistory.egg-info')


@task
def pympler(context):
    """Run memory profiler interactively."""
    memory_tracker = tracker.SummaryTracker()
    while input('Get memory diff? ') != NEGATIVE:
        memory_tracker.print_diff()


@task
def restore_squashed_migrations(context):
    """Restore migrations with squashed_migrations."""
    commands.restore_squashed_migrations(context)


@task
def setup(context, noninteractive: bool = False):
    """Install all dependencies; set up the ModularHistory application."""
    args = [relativize('setup.sh')]
    if noninteractive:
        args.append('--noninteractive')
    command = SPACE.join(args).strip()
    context.run(command)
    context.run('rm -r modularhistory.egg-info')


@task
def squash_migrations(context, dry: bool = True):
    """Squash migrations."""
    commands.squash_migrations(context, dry)


@task
def test(context, docker=False):
    """Run tests."""
    commands.escape_prod_db()
    pytest_args = [
        '-v',
        '-n 3',
        # '-x',
        '--maxfail=2',
        # '--hypothesis-show-statistics',
    ]
    command = f'coverage run -m pytest {" ".join(pytest_args)}'
    print(command)
    if docker:
        context.run(
            'docker build -t modularhistory/modularhistory . && docker-compose up'
        )
    context.run(command)
    context.run('rm -r archived_logs && mv latest_logs .selenium')
    context.run('coverage combine')
