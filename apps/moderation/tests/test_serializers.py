import pytest

from apps.moderation.serializers import ModeratedModelSerializer

from .moderated_serializers import MODERATED_SERIALIZERS as serializers


@pytest.mark.django_db()
class TestModeratedSerializers:
    def test_moderated_fields(self):
        assert len(serializers) > 0, 'No serializers found'

        for serializer in serializers:
            assert not isinstance(
                serializer, ModeratedModelSerializer
            ), 'Serializer is not a ModeratedModelSerializer'

            for field in serializer().get_moderated_fields():
                assert field['name'], 'Field name is empty'
                # TODO: add more tests here
