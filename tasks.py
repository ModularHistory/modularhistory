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

import errno
import linecache
import os
import tracemalloc
from typing import Any, Callable, TypeVar

import django

from modularhistory import settings
from modularhistory.constants.strings import NEGATIVE, SPACE
from modularhistory.linters import flake8 as lint_with_flake8, mypy as lint_with_mypy
from modularhistory.utils import commands
from modularhistory.utils.files import relativize
from monkeypatch import fix_annotations

tracemalloc.start(25)

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

    from topics.models import Topic

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

    print('Building detail artifacts...')
    from occurrences.models import Occurrence
    from quotes.models import Quote

    models_with_artifacts = (Occurrence, Quote)
    for model_cls in models_with_artifacts:
        app_name = model_cls.get_meta().app_label.lower()
        for model_instance in model_cls.objects.all().iterator():
            detail_html = model_instance.generate_html_for_view()
            artifact_name = f'{model_instance.pk}.html'
            artifact_dir = os.path.join(
                settings.BASE_DIR, app_name, 'artifacts/details'
            )
            artifact_path = os.path.join(artifact_dir, artifact_name)
            if not os.path.exists(artifact_dir):
                try:
                    os.makedirs(artifact_dir)
                except OSError as error:  # Guard against race condition
                    if error.errno != errno.EEXIST:
                        raise
            with open(artifact_path, mode='w') as artifact:
                artifact.write(detail_html)


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
def restore_squashed_migrations(context):
    """Restore migrations with squashed_migrations."""
    commands.restore_squashed_migrations(context)


@task
def test(context):
    """Run tests."""
    ref_snapshot = tracemalloc.take_snapshot()
    commands.escape_prod_db()
    pytest_args = [
        '-v',
        '-n 3',
        # '-x',
        '--maxfail=2',
        # '--hypothesis-show-statistics',
        '--disable-warnings',
    ]
    command = f'coverage run -m pytest {" ".join(pytest_args)}'
    print(command)
    context.run(command)
    snapshot = tracemalloc.take_snapshot()
    traces = snapshot.statistics('traceback')
    for index, stat in enumerate(snapshot.compare_to(ref_snapshot, 'lineno')[:15]):
        diff = f'{stat}'
        filters = (
            '<frozen importlib._bootstrap' not in diff,
            'linecache' not in diff,
            'autoreload.py' not in diff,
        )
        if all(filters):
            print(diff)
            trace = traces[index]
            print("%s memory blocks: %.1f KiB" % (stat.count, stat.size / 1024))
            for line in trace.traceback.format():
                print(line)
        print()
    # display_top(snapshot)
    context.run('coverage combine')


@task
def deploy(context):
    """Run linters."""
    # TODO
    is_implemented = False
    if is_implemented:
        context.run('python manage.py collectstatic')
        app_file = 'gc_app.yaml'
        env_file = 'gc_env.yaml'
        perm_env_file = 'gc_env.yaml.perm'
        temp_env_file = 'gc_env.yaml.tmp'
        # TODO: load secrets to env
        context.run(
            f'cp {env_file} {perm_env_file} && envsubst < {env_file} > {temp_env_file} '
            f'&& mv {temp_env_file} {env_file} && gcloud app deploy {app_file}'
        )
        context.run(f'mv {perm_env_file} {env_file}')
    else:
        raise NotImplementedError


def display_top(snapshot, key_type='lineno', limit=15):
    snapshot = snapshot.filter_traces((
        tracemalloc.Filter(False, "<frozen importlib._bootstrap>"),
        tracemalloc.Filter(False, "<frozen importlib._bootstrap_external>"),
        tracemalloc.Filter(False, "<unknown>"),
    ))
    top_stats = snapshot.statistics(key_type)

    print("Top %s lines" % limit)
    for index, stat in enumerate(top_stats[:limit], 1):
        frame = stat.traceback[0]
        print("#%s: %s:%s: %.1f KiB"
              % (index, frame.filename, frame.lineno, stat.size / 1024))
        line = linecache.getline(frame.filename, frame.lineno).strip()
        if line:
            print('    %s' % line)

    other = top_stats[limit:]
    if other:
        size = sum(stat.size for stat in other)
        print("%s other: %.1f KiB" % (len(other), size / 1024))
    total = sum(stat.size for stat in top_stats)
    print("Total allocated size: %.1f KiB" % (total / 1024))
