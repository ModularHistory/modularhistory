"""Serializers for the CMS app."""

from rest_framework import serializers

from apps.cms.models import Branch, PullRequest


class BranchSerializer(serializers.ModelSerializer):
    """Serializer for branches."""

    class Meta:
        model = Branch
        exclude = []


class PullRequestSerializer(serializers.ModelSerializer):
    """Serializer for pull requests."""

    source_branch = BranchSerializer()
    target_branch = BranchSerializer()

    class Meta:
        model = PullRequest
        exclude = []
