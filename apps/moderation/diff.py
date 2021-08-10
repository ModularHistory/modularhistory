import difflib
import re
from typing import TYPE_CHECKING

from django.db.models import ImageField, fields
from django.db.models.fields.related import ForeignObject
from django.utils.html import escape

if TYPE_CHECKING:
    from apps.moderation.models.moderated_model import ModeratedModel


class FieldChange:
    """Base class for a change to a field's value."""

    def __init__(self, verbose_name: str, field, before_and_after: tuple):
        self.verbose_name = verbose_name
        self.field = field
        self.change = before_and_after

    def __repr__(self) -> str:
        value_before, value_after = self.change
        return f'Change object: {value_before} - {value_after}'

    def render_diff(self, template, context) -> str:
        from django.template.loader import render_to_string

        return render_to_string(template, context)


class TextChange(FieldChange):
    """A change to the value of a text field."""

    @property
    def diff(self) -> str:
        """Render the diff."""
        value_before, value_after = escape(self.change[0]), escape(self.change[1])
        if value_before == value_after:
            return value_before
        return self.render_diff(
            template='moderation/changes/html_diff.html',
            context={'diff_operations': get_diff_operations(*self.change)},
        )


class ImageChange(FieldChange):
    """A change to the value of an image field."""

    @property
    def diff(self) -> str:
        """Render the diff."""
        left_image, right_image = self.change
        return self.render_diff(
            'moderation/image_diff.html',
            {'left_image': left_image, 'right_image': right_image},
        )


def get_field_change(
    field: fields.Field,
    object_before_change: 'ModeratedModel',
    object_after_change: 'ModeratedModel',
    resolve_foreignkeys: bool = True,
) -> FieldChange:
    """Return a FieldChange object for the field."""
    try:
        value_before = getattr(object_before_change, f'get_{field.name}_display')()
        value_after = getattr(object_after_change, f'get_{field.name}_display')()
    except AttributeError:
        if isinstance(field, ForeignObject) and resolve_foreignkeys:
            value_before = str(getattr(object_before_change, field.name))
            value_after = str(getattr(object_after_change, field.name))
        else:
            value_before = field.value_from_object(object_before_change)
            value_after = field.value_from_object(object_after_change)
    if isinstance(field, ImageField):
        change = ImageChange(
            f'Current {field.verbose_name} / New {field.verbose_name}',
            field=field,
            before_and_after=(value_before, value_after),
        )
    else:
        change = TextChange(
            field.verbose_name,
            field=field,
            before_and_after=(str(value_before), str(value_after)),
        )
    return change


def get_changes_between_models(
    object_before_change: 'ModeratedModel',
    object_after_change: 'ModeratedModel',
    excluded_fields=None,
    included_fields=None,
    resolve_foreignkeys=False,
) -> dict:
    changes = {}
    if excluded_fields is None:
        excluded_fields = []
    if included_fields is None:
        included_fields = []
    field: fields.Field
    for field in object_before_change._meta.fields:
        if any(
            [
                included_fields and field.name not in included_fields,
                field.name in excluded_fields,
                isinstance(field, (fields.AutoField,)),
            ]
        ):
            continue
        name = f'{object_before_change.__class__.__name__.lower()}__{field.name}'
        changes[name] = get_field_change(
            field, object_before_change, object_after_change, resolve_foreignkeys
        )
    return changes


def get_diff_operations(a, b) -> list:
    operations = []
    a_words = re.split(r'(\W+)', a)
    b_words = re.split(r'(\W+)', b)
    sequence_matcher = difflib.SequenceMatcher(None, a_words, b_words)
    for opcode in sequence_matcher.get_opcodes():
        operation, start_a, end_a, start_b, end_b = opcode
        deleted = ''.join(a_words[start_a:end_a])
        inserted = ''.join(b_words[start_b:end_b])
        operations.append({'operation': operation, 'deleted': deleted, 'inserted': inserted})
    return operations


def html_to_list(html) -> list:
    pattern = re.compile(
        r'&.*?;|(?:<[^<]*?>)|' r'(?:\w[\w-]*[ ]*)|(?:<[^<]*?>)|' r'(?:\s*[,\.\?]*)',
        re.UNICODE,
    )
    return [''.join(element) for element in [_f for _f in pattern.findall(html) if _f]]
