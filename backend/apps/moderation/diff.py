import difflib
import logging
import re
from typing import TYPE_CHECKING, Optional

from django.core.exceptions import FieldError
from django.db.models import ImageField, fields
from django.db.models.fields.related import ForeignObject, ManyToManyField, OneToOneField
from django.db.models.fields.reverse_related import ManyToManyRel, ManyToOneRel, OneToOneRel
from django.template.loader import render_to_string
from django.utils.html import escape

from apps.moderation.models import Change

if TYPE_CHECKING:
    from django.db.models.query import QuerySet

    from apps.moderation.models.moderated_model import ModeratedModel
    from core.models.relations.moderated import ModeratedRelation


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
            'moderation/changes/image_diff.html',
            {'left_image': self.before, 'right_image': self.after},
        )


class RelationsChange(FieldChange):
    """A change to the value of a m2m field."""

    @property
    def diff(self) -> str:
        """Render the diff."""
        if self.before == self.after:
            diffs = self.before
        else:
            control_strings = ('---', '+++', '@@')
            diffs = [
                diff
                for diff in difflib.unified_diff(self.before, self.after)
                if not diff.startswith(control_strings)
            ]
        return self.render_diff(
            template='moderation/changes/m2m_diff.html',
            context={'diff_items': diffs},
        )


def get_field_change(
    field: fields.Field,
    change: 'Change',
    resolve_foreignkeys: bool = True,
) -> FieldChange:
    """Return a FieldChange object for the field."""
    object_after_change: ModeratedModel = change.changed_object
    object_before_change: ModeratedModel = change.unchanged_object
    try:
        value_before = getattr(object_before_change, f'get_{field.name}_display')()
        value_after = getattr(object_after_change, f'get_{field.name}_display')()
    except AttributeError:
        if isinstance(field, (OneToOneRel, OneToOneField)) and resolve_foreignkeys:
            value_before = getattr(object_before_change, field.name, '') or ''
            value_after = getattr(object_after_change, field.name, '') or ''
            return RelationsChange(
                field.verbose_name,
                field=field,
                before_and_after=(value_before, value_after),
            )
        elif isinstance(field, (ManyToManyRel, ManyToManyField)):  # TODO: refactor
            relation_kwargs = {f'{field.m2m_column_name()}': object_before_change.pk}
            relations: 'QuerySet[ModeratedRelation]' = (
                field.remote_field.through.objects.filter(**relation_kwargs)
            )
            relation_changes = Change.objects.filter(parent=change)
            try:
                changed_relation_ids = relation_changes.values_list('object_id', flat=True)
                modified_relations = relations.filter(id__in=changed_relation_ids)
                added_relations = modified_relations.filter(deleted__isnull=True)
                # TODO: changed_relations
                deleted_relations = field.remote_field.through.objects.filter(
                    id__in=[
                        change.object_id
                        for change in relation_changes.all()
                        if change.changed_object.deleted
                    ]
                )
                added_relations = modified_relations.filter(deleted__isnull=True).difference(
                    deleted_relations
                )
                relations_before = relations.difference(added_relations)
                relations_after = relations.difference(deleted_relations)
                value_before = [str(related_object) for related_object in relations_before]
                value_after = [str(related_object) for related_object in relations_after]
            except FieldError as err:
                logging.error(err)
                value_before = value_after = ''
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
            field.verbose_name,
            field=field,
            before_and_after=(value_before, value_after),
        )
    if value_before is None:
        value_before = ''
    if value_after is None:
        value_after = ''
    return TextChange(
        getattr(field, 'verbose_name', getattr(field, 'related_name', '')),
        field=field,
        before_and_after=(str(value_before), str(value_after)),
    )


def get_field_changes(
    change: 'Change',
    excluded_fields: Optional[list] = None,
    included_fields: Optional[list] = None,
    resolve_foreignkeys: bool = True,
) -> dict:
    content_object: ModeratedModel = change.content_object
    changes = {}
    if excluded_fields is None:
        excluded_fields = []
    if included_fields is None:
        included_fields = []
    field: fields.Field
    for field in content_object._meta.get_fields():
        if any(
            [
                field.name in excluded_fields,
                included_fields and field.name not in included_fields,
                getattr(field, 'verbose_name', None) is None,
                isinstance(field, (fields.AutoField,)),
            ]
        ):
            continue
        name = f'{content_object.__class__.__name__.lower()}__{field.name}'
        changes[name] = get_field_change(field, change, resolve_foreignkeys)
    return changes


def get_diff_operations(a: str, b: str) -> list:
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
