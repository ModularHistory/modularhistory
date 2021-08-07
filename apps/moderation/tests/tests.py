import pytest
from django.contrib.contenttypes.models import ContentType

from apps.moderation.models.change import Change
from apps.propositions.models import Proposition


@pytest.mark.django_db()
class TestModeration:
    """Test the moderation app."""

    def test_making_a_change(self):
        """
        Test making a change to a moderated model instance.
        """
        original_summary = 'summary'
        changed_summary = 'changed summary'
        p = Proposition(
            type='propositions.conclusion',
            summary=original_summary,
            elaboration='<p>elaboration</p>',
            certainty=1,
        )
        p.save()
        p.summary = changed_summary
        change = Change(
            content_type=ContentType.objects.get_for_model(Proposition),
            object_id=p.pk,
            changed_object=p,
        )
        assert change.changed_object.summary == changed_summary
        change.save()
        change.refresh_from_db()
        assert change.changed_object.summary == changed_summary
        p.refresh_from_db()
        assert p.summary == original_summary
