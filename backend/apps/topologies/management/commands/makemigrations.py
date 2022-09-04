import os
import re
from glob import glob

from django.conf import settings
from django.core.management.commands.makemigrations import (
    Command as CoreMakeMigrationsCommand,
)
from django.db.migrations.operations import AddField, CreateModel

from apps.topologies.fields import LtreeField

# Match the beginning of the dependencies list in a migration file
# so that the initial migration of the topologies app can be inserted.
DEPENDENCIES_PATTERN = r'dependencies = \['

# Match content beginning with `operations = [` and ending before the linebreak
# and closing bracket of the operations list in a migration file.
# `migrations.RunSQL` operations are appended to the matched content.
OPERATIONS_PATTERN = r'operations = \[(?!\w+\ =)[\s\S]+(?=\n\s+\])'


def get_sql(app_name: str, model_name: str):
    """Return the SQL code that must be run to configure a new TreeModel."""
    sql_scripts = []
    for filename in ('indexes.sql', 'constraints.sql'):
        filepath = os.path.join(settings.BASE_DIR, 'apps/topologies/sql', filename)
        with open(filepath) as f:
            sql_scripts.append(
                f.read().format(app_name=app_name, model_name=model_name).strip()
            )
    return '\n\n'.join(sql_scripts)


def insert_topologies_dependency(migration_file_content: str) -> str:
    """
    Given the content of a migration file that adds a TreeModel,
    insert the topologies app's initial migration as a dependency.
    Return the modified migration file content.
    """
    dependencies = re.search(DEPENDENCIES_PATTERN, migration_file_content)
    if dependencies:
        dependencies_content = dependencies.group(0)
        migration_file_content = migration_file_content.replace(
            dependencies_content,
            f'{dependencies_content}\n' "        ('topologies', '0001_initial'),",
        )
    else:
        raise Exception(
            'Unable to add topologies migration dependency to '
            f'{migration_file_content}; the regex expression '
            f'{DEPENDENCIES_PATTERN} found no match in the file.'
        )
    return migration_file_content


def insert_run_sql_operation(
    migration_file_content: str, app_name: str, model_name: str
) -> str:
    """
    Given the content of a migration file that adds a TreeModel (and the app_name
    and model_name for the TreeModel to be created), insert a RunSQL operation
    to make the new TreeModel work correctly (with constraints, indexes, etc.).
    """
    operations = re.search(OPERATIONS_PATTERN, migration_file_content)
    if operations:
        operations_content = operations.group(0)
        sql = get_sql(app_name=app_name, model_name=model_name)
        migration_file_content = migration_file_content.replace(
            operations_content,
            f'{operations_content}\n'
            '        '
            f'migrations.RunSQL("""\n{sql}\n"""\n'
            '        ),',
        )
    else:
        raise Exception(
            'Unable to add necessary RunSQL operation to '
            f'{migration_file_content}; the regex expression '
            f'{OPERATIONS_PATTERN} found no match in the file.'
        )
    return migration_file_content


class Command(CoreMakeMigrationsCommand):
    def write_migration_files(self, changes):
        super().write_migration_files(changes)
        # If adding an LtreeField, modify the migration file as necessary.
        for app, app_changes in changes.items():
            migration_files = glob(os.path.join('apps', app, 'migrations', '*.py'))
            migration_filepath = max(migration_files, key=os.path.getctime)
            for app_change in app_changes:
                for operation in app_change.operations:
                    adding_an_ltree_field = False
                    if isinstance(operation, CreateModel):
                        adding_an_ltree_field = any(
                            isinstance(field, LtreeField) for _, field in operation.fields
                        )
                        model_name = operation.name_lower
                    elif isinstance(operation, AddField):
                        adding_an_ltree_field = isinstance(
                            operation.__dict__['field'], LtreeField
                        )
                        model_name = operation.model_name_lower
                    if not adding_an_ltree_field:
                        continue
                    if self.dry_run:
                        print(
                            'The migration file will need to be modified '
                            'to accommodate our TreeModel fields.'
                        )
                        return
                    with open(migration_filepath, 'r') as migration_file:
                        migration_file_content = migration_file.read()
                    migration_file_content = insert_topologies_dependency(
                        migration_file_content
                    )
                    migration_file_content = insert_run_sql_operation(
                        migration_file_content, app_name=app, model_name=model_name
                    )
                    with open(migration_filepath, 'w') as migration_file:
                        migration_file.write(migration_file_content)
