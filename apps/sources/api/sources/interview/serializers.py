from apps.sources.api.serializers import SourceDrfSerializer
from apps.sources.models import Interview


class InterviewDrfSerializer(SourceDrfSerializer):
    """Serializer for interview sources."""

    class Meta(SourceDrfSerializer.Meta):
        model = Interview
        fields = SourceDrfSerializer.Meta.fields + [
            'interviewers',
        ]
