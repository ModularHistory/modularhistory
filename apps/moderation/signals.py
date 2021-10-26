from django.db.models import Q, QuerySet

from apps.moderation.models import ModeratedModel


def process_relation_changes(
    sender: ModeratedModel,
    instance: ModeratedModel,
    related_field_name,
    relations: QuerySet,
    **kwargs,
):
    action = kwargs.pop('action', None)
    related_ids = kwargs.pop('pk_set', set())

    if action == 'post_add':
        related_filter = Q(**{f'{related_field_name}__in': related_ids})
        # re-save newly added relations to trigger moderation
        for relation in relations.filter(related_filter):
            relation.save()
