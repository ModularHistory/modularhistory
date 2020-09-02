from rest_framework import serializers

from entities.models import Entity


# TODO: https://www.valentinog.com/blog/drf/

class EntitySerializer(serializers.ModelSerializer):
    """TODO: add docstring."""

    class Meta:
        model = Entity
        fields = [
            'name',
            'verbose_name',
            'aliases',
            'birth_date',
            'death_date',
            'description',
            'classifications',
            'images',
            'affiliated_entities',
        ]
