import os
import re
from glob import glob

from django.conf import settings
from django.core.management.commands.makemigrations import (
    Command as CoreMakeMigrationsCommand,
)
from django.db.migrations.operations.fields import AddField

from apps.trees.fields import LtreeField

# Match the beginning of the dependencies list in a migration file
# so that the initial migration of the trees app can be inserted.
DEPENDENCIES_PATTERN = r'dependencies = \['

# Match content beginning with `operations = [` and ending before the linebreak
# and closing bracket of the operations list in a migration file.
# `migrations.RunSQL` operations are appended to the matched content.
OPERATIONS_PATTERN = r'operations = \[[\s\n]+((migrations.[A-Z][\s\S]+?(?=migrations.[A-Z]\w+|\n?\s*\]))+)'


def get_sql(app_name: str, model_name: str):
    sql_scripts = []
    for filename in ('index.sql', 'constraint.sql', 'triggers.sql'):
        filepath = os.path.join(settings.BASE_DIR, 'apps/trees/sql', filename)
        with open(filepath) as f:
            sql_scripts.append(
                f.read().format(app_name=app_name, model_name=model_name).strip()
            )
    return '\n\n'.join(sql_scripts)


class Command(CoreMakeMigrationsCommand):
    def write_migration_files(self, changes):
        super().write_migration_files(changes)
        for app, app_changes in changes.items():
            migration_files = glob(os.path.join('apps', app, 'migrations', '*.py'))
            migration_filepath = max(migration_files, key=os.path.getctime)
            for app_change in app_changes:
                for operation in app_change.operations:
                    # If adding an LtreeField, prompt to add a RunSQL operation
                    # to the migration file.
                    adding_an_ltree_field = isinstance(
                        operation, AddField
                    ) and isinstance(operation.__dict__.get('field'), LtreeField)
                    if not adding_an_ltree_field:
                        continue
                    model_name = operation.model_name_lower
                    with open(migration_filepath, 'r') as migration_file:
                        migration_content = migration_file.read()
                    dependencies = re.search(DEPENDENCIES_PATTERN, migration_content)
                    if dependencies:
                        dependencies_content = dependencies.group(0)
                        migration_content = migration_content.replace(
                            dependencies_content,
                            f'{dependencies_content}\n'
                            "        ('trees', '0001_initial'),",
                        )
                    else:
                        raise Exception(
                            'Unable to add trees migration dependency to '
                            f'{migration_filepath}; the regex expression '
                            f'{DEPENDENCIES_PATTERN} found no match in the file.'
                        )
                    operations = re.search(OPERATIONS_PATTERN, migration_content)
                    if operations:
                        operations_content = operations.group(0)
                        sql = get_sql(app_name=app, model_name=model_name)
                        migration_content = migration_content.replace(
                            operations_content,
                            f'{operations_content}\n'
                            '        '
                            f'migrations.RunSQL("""\n{sql}"""\n'
                            '        ),',
                        )
                        with open(migration_filepath, 'w') as migration_file:
                            migration_file.write(migration_content)
                    else:
                        raise Exception(
                            'Unable to add necessary RunSQL operation to '
                            f'{migration_filepath}; the regex expression '
                            f'{OPERATIONS_PATTERN} found no match in the file.'
                        )
