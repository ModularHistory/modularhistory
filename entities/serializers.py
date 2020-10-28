"""Serializers for the entities app."""

# TODO: https://medium.com/better-programming/how-to-use-drf-serializers-effectively-dc58edc73998
# TODO: https://www.valentinog.com/blog/drf/

from rest_framework import serializers

from entities.models import Entity


class EntitySerializer(serializers.ModelSerializer):
    """Serializer for entities."""

    class Meta:
        model = Entity
        fields = [
            'name',
            'verbose_name',
            'aliases',
            'birth_date',
            'death_date',
            'description',
            'categories',
            'images',
            'affiliated_entities',
        ]
