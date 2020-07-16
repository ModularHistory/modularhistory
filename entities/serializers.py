from rest_framework import serializers
from .models import Entity


# TODO: https://www.valentinog.com/blog/drf/

class EntitySerializer(serializers.ModelSerializer):
    class Meta:
        model = Entity
        # fields = (
        #     'name',
        #     'birth_date',
        #     'death_date',
        # )
