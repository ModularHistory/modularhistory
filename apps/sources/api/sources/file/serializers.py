import filetype
from django.utils.translation import gettext_lazy as _
from drf_extra_fields.fields import Base64FileField
from rest_framework import serializers

from apps.sources.models import SourceFile
from core.models.model import ModelSerializer


class SourceFileBase64Field(Base64FileField):

    # TODO: add additional file types if needed
    ALLOWED_TYPES = ['pdf', 'epub', 'jpeg', 'jpg', 'png', 'gif']
    INVALID_FILE_MESSAGE = _("Uploaded file has invalid type '{}', allowed types are: {}")

    def get_file_extension(self, filename, decoded_file):
        guessed_extension = filetype.guess_extension(decoded_file)
        if guessed_extension not in self.ALLOWED_TYPES:
            raise serializers.ValidationError(
                self.INVALID_FILE_MESSAGE.format(
                    guessed_extension, ', '.join(self.ALLOWED_TYPES)
                )
            )
        return guessed_extension


class SourceFileDrfSerializer(ModelSerializer):
    """Serializer for sources files."""

    file = SourceFileBase64Field()

    class Meta:
        model = SourceFile
        fields = ModelSerializer.Meta.fields + [
            'file',
            'name',
            'page_offset',
            'first_page_number',
            'uploaded_at',
        ]
        read_only_fields = ['uploaded_at']
        extra_kwargs = {'file': {'required': True}}
