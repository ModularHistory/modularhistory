import difflib
import re
from typing import TYPE_CHECKING, Optional

from django.db.models import ImageField, fields
from django.db.models.fields.related import ForeignObject, ManyToManyField, OneToOneField
from django.db.models.fields.reverse_related import ManyToManyRel, ManyToOneRel, OneToOneRel
from django.template.loader import render_to_string
from django.utils.html import escape

if TYPE_CHECKING:
    from apps.moderation.models.moderated_model import ModeratedModel


class FieldChange:
    """Base class for a change to a field's value."""

    def __init__(self, verbose_name: str, field: fields.Field, before_and_after: tuple):
        self.verbose_name = verbose_name
        self.field = field
        self.before = before_and_after[0]
        self.after = before_and_after[1]

    def __repr__(self) -> str:
        return f'Change object: {self.before} - {self.after}'

    def render_diff(self, template, context) -> str:
        return render_to_string(template, context)


class TextChange(FieldChange):
    """A change to the value of a text field."""

    @property
    def diff(self) -> str:
        """Render the diff."""
        value_before, value_after = escape(self.before), escape(self.after)
        if value_before == value_after:
            return value_before
        return self.render_diff(
            template='moderation/changes/html_diff.html',
            context={'diff_operations': get_diff_operations(self.before, self.after)},
        )


class ImageChange(FieldChange):
    """A change to the value of an image field."""

    @property
    def diff(self) -> str:
        """Render the diff."""
        return self.render_diff(
            'moderation/image_diff.html',
            {'left_image': self.before, 'right_image': self.after},
        )


class RelationsChange(FieldChange):
    """A change to the value of a m2m field."""

    @property
    def diff(self) -> str:
        """Render the diff."""
        print()
        print(f'Before: {self.before}\nAfter: {self.after}')
        if self.before == self.after:
            diffs = self.before
        else:
            print('Diffs:')
            for diff in difflib.unified_diff(self.before, self.after):
                print(diff)
            diffs = [diff for diff in difflib.unified_diff(self.before, self.after)]
            # print(diffs)
        print()
        return self.render_diff(
            template='moderation/changes/m2m_diff.html',
            context={'diff_items': diffs},
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
        if isinstance(field, (OneToOneRel, OneToOneField)) and resolve_foreignkeys:
            try:
                value_before = str(getattr(object_before_change, field.name))
            except field.related_model.DoesNotExist:
                value_before = ''
            try:
                value_after = str(getattr(object_after_change, field.name))
            except field.related_model.DoesNotExist:
                value_after = ''
            return RelationsChange(
                field.related_name,
                field=field,
                before_and_after=(value_before, value_after),
            )
        elif isinstance(field, (ManyToManyRel, ManyToManyField)):
            value_before = [
                str(related_object)
                for related_object in getattr(object_before_change, field.name).all()
            ]
            value_after = [
                str(related_object)
                for related_object in getattr(object_after_change, field.name).all()
            ]
            return RelationsChange(
                field.verbose_name,
                field=field,
                before_and_after=(value_before, value_after),
            )
        elif isinstance(field, (ForeignObject, ManyToOneRel)) and resolve_foreignkeys:
            value_before = str(getattr(object_before_change, field.name))
            value_after = str(getattr(object_after_change, field.name))
        else:
            value_before = field.value_from_object(object_before_change)
            value_after = field.value_from_object(object_after_change)
    if isinstance(field, ImageField):
        return ImageChange(
            f'Current {field.verbose_name} / New {field.verbose_name}',
            field=field,
            before_and_after=(value_before, value_after),
        )
    return TextChange(
        getattr(field, 'verbose_name', getattr(field, 'related_name', '')),
        field=field,
        before_and_after=(str(value_before), str(value_after)),
    )


def get_changes_between_models(
    object_before_change: 'ModeratedModel',
    object_after_change: 'ModeratedModel',
    excluded_fields: Optional[list] = None,
    included_fields: Optional[list] = None,
    resolve_foreignkeys: bool = True,
) -> dict:
    changes = {}
    if excluded_fields is None:
        excluded_fields = []
    if included_fields is None:
        included_fields = []
    field: fields.Field
    for field in object_before_change._meta.get_fields():
        if any(
            [
                field.name in excluded_fields,
                included_fields and field.name not in included_fields,
                getattr(field, 'verbose_name', None) is None,
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
