from typing import TYPE_CHECKING, Type

from django.db.models import Count, Q
from django.db.models.manager import Manager

from apps.moderation.models.change import Change
from core.models.manager import SearchableManager

if TYPE_CHECKING:
    from apps.moderation.models.moderated_model import (
        ModeratedModel,
        SearchableModeratedModel,
    )


class ModeratedModelManager(Manager):
    """Manager for moderated models."""

    model: Type['ModeratedModel']

    def filter_moderations(self, queryset):
        # Find any objects that have more than one related Moderation
        annotated_queryset = queryset.annotate(
            num_moderation_objects=Count('_relation_object')
        ).filter(num_moderation_objects__gt=1)

        if annotated_queryset.exists():
            # No sensible default action here. You need to override
            # filter_moderations() to handle this as you see fit.
            raise self.MultipleModerations(annotated_queryset)

        only_no_relation_objects = {
            '_relation_object': None,
        }
        only_ready = {
            '_relation_object__state': Change.DraftState.READY.value,
        }
        return queryset.filter(Q(**only_no_relation_objects) | Q(**only_ready))


class SearchableModeratedModelManager(SearchableManager, ModeratedModelManager):
    """Manager for moderated models of which users can search for instances."""

    model: Type['SearchableModeratedModel']
