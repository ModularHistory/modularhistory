from rest_framework import serializers
from rest_framework.serializers import ModelSerializer

from apps.moderation.models.contribution import ContentContribution


class ContentContributionSerializer(serializers.ModelSerializer):
    """Serializer for ContentContribution."""

    class Meta:
        model = ContentContribution
        fields = '__all__'
