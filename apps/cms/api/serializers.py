"""Serializers for the CMS app."""

from rest_framework import serializers

from apps.cms.models import Branch


class BranchSerializer(serializers.ModelSerializer):
    """Serializer for branches."""

    class Meta:
        model = Branch
        exclude = []
