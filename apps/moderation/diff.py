# -*- coding: utf-8 -*-

import difflib
import re

from django.db.models import ImageField, fields
from django.db.models.fields.related import ForeignObject
from django.utils.html import escape


class FieldChange:
    """Base class for a change to a field's value."""

    def __repr__(self):
        value1, value2 = self.change
        return 'Change object: {} - {}'.format(value1, value2)

    def __init__(self, verbose_name, field, before_and_after: tuple):
        self.verbose_name = verbose_name
        self.field = field
        self.change = before_and_after

    def render_diff(self, template, context):
        from django.template.loader import render_to_string

        return render_to_string(template, context)


class TextChange(FieldChange):
    """A change to the value of a text field."""

    @property
    def diff(self) -> str:
        """Render the diff."""
        value1, value2 = escape(self.change[0]), escape(self.change[1])
        if value1 == value2:
            return value1

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


def get_change(field, model1, model2, resolve_foreignkeys=False) -> FieldChange:
    """Return a FieldChange object for the field."""
    try:
        value1 = getattr(model1, f'get_{field.name}_display')()
        value2 = getattr(model2, f'get_{field.name}_display')()
    except AttributeError:
        if isinstance(field, ForeignObject) and resolve_foreignkeys:
            value1 = str(getattr(model1, field.name))
            value2 = str(getattr(model2, field.name))
        else:
            value1 = field.value_from_object(model1)
            value2 = field.value_from_object(model2)
    return get_change_for_type(
        field.verbose_name,
        (value1, value2),
        field,
    )


def get_changes_between_models(
    object_before_change,
    object_after_change,
    excluded_fields=None,
    included_fields=None,
    resolve_foreignkeys=False,
) -> dict:
    changes = {}
    if excluded_fields is None:
        excluded_fields = []
    if included_fields is None:
        included_fields = []
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
        changes[name] = get_change(
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


def get_change_for_type(
    verbose_name: str,
    before_and_after: tuple,
    field: fields.Field,
) -> FieldChange:
    if isinstance(field, ImageField):
        change = ImageChange(
            f'Current {verbose_name} / New {verbose_name}',
            field=field,
            before_and_after=before_and_after,
        )
    else:
        value1, value2 = before_and_after
        change = TextChange(
            verbose_name,
            field=field,
            before_and_after=(str(value1), str(value2)),
        )
    return change
