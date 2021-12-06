import sys

import pytest
from django.contrib.contenttypes.models import ContentType

from apps.dates.structures import HistoricDateTime
from apps.moderation.models.change import Change
from apps.moderation.tasks import handle_approval
from apps.propositions.models import Proposition, TopicRelation
from apps.topics.models import Topic
from apps.users.factories import UserFactory
from core.environment import TESTING


@pytest.mark.django_db()
class TestModeration:
    """Test the moderation app."""

    def test_making_change(self):
        """Test making a change to a moderated model instance."""
        title = 'title'
        original_summary = 'summary'
        changed_summary = 'changed summary'

        # Create and save a model instance.
        p = Proposition(
            type='propositions.conclusion',
            title=title,
            summary=original_summary,
            elaboration='<p>elaboration</p>',
            certainty=1,
            date=HistoricDateTime(2000, 1, 1, 1, 1, 1, microsecond=1),
        )
        p.save(contributor=UserFactory.create())

        proposition_ct = ContentType.objects.get_for_model(Proposition)

        # Create and save a `Change` instance in which a field is modified.
        p.summary = changed_summary
        change = Change(
            content_type=proposition_ct,
            object_id=p.pk,
            changed_object=p,
        )
        assert change.changed_object.summary == changed_summary
        change.save()

        # Modify another field.
        changed_title = 'changed title'
        change.changed_object.title = changed_title
        change.save()

        # Verify the change state is separate from the model instance state.
        change.refresh_from_db()
        p.refresh_from_db()
        assert change.changed_object.summary == changed_summary
        assert p.summary == original_summary
        assert change.changed_object.title == changed_title
        assert change.changed_object.title != p.title
        assert change.changed_object.date == change.content_object.date

        # Test adding a m2m relationship.
        assert TESTING, f'{sys.argv}'
        topic = Topic.objects.create(name='test topic', verified=True)
        relation = TopicRelation(topic=topic, content_object=p)
        relation_change = relation.save_change(parent_change=change)
        assert not relation.verified
        assert relation.has_change_in_progress
        assert relation.change_in_progress.parent == change
        topic_relations = p.topic_relations.all()
        assert not topic_relations.exists(), f'{type(topic_relations)}: {topic_relations}'

        # Test approving the change.
        for _ in range(change.n_required_approvals):
            moderator = UserFactory.create()
            approval = change.approve(moderator=moderator)
            handle_approval(approval.pk)
        relation_approval = relation_change.moderations.first()
        handle_approval(relation_approval.pk)
        change.refresh_from_db()
        relation_change.refresh_from_db()
        assert change.merged_date, f'{change.n_remaining_approvals_required=}'
        assert (
            relation_change.merged_date
        ), f'{relation_change.n_remaining_approvals_required=}'
        assert p.topic_relations.exists()
        assert p.topic_relations.first().topic == topic
