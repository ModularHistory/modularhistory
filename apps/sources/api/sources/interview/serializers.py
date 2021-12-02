from apps.sources.api.serializers import SourceSerializer
from apps.sources.models import Interview


class InterviewSerializer(SourceSerializer):
    """Serializer for interview sources."""

    class Meta(SourceSerializer.Meta):
        model = Interview
        fields = SourceSerializer.Meta.fields + [
            'interviewers',
        ]
