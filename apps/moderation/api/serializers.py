from rest_framework import serializers

from apps.moderation.models import Change, ContentContribution


class ChangeSerializer(serializers.ModelSerializer):

    content_object = serializers.SerializerMethodField()

    class Meta:
        model = Change
        fields = ('content_object',)

    def get_content_object(self, obj: Change):
        return obj.content_object.serialize()


class ContentContributionSerializer(serializers.ModelSerializer):
    """Serializer for ContentContribution."""

    absolute_url = serializers.CharField(required=False, read_only=True)
    change = ChangeSerializer(read_only=True)

    class Meta:
        model = ContentContribution
        # fields = '__all__'
        fields = ('id', 'contributor', 'absolute_url', 'change')
