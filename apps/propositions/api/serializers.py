from apps.propositions.models import Argument, Occurrence, Proposition
from core.models.model import ModelSerializerDrf
from core.models.module import ModuleSerializerDrf


class _PropositionModelSerializer(ModuleSerializerDrf):
    """Serializer for propositions."""

    def get_model(self, instance) -> str:
        """Return the model name of serialized propositions."""
        return 'propositions.proposition'

    class Meta(ModuleSerializerDrf.Meta):
        model = Proposition
        fields = ModuleSerializerDrf.Meta.fields + [
            'summary',
            'elaboration',
            'certainty',
            'date_string',
            'tags_html',
            'cached_citations',
            'primary_image',
            'cached_images',
        ]
        extra_kwargs = {'certainty': {'required': False}}


class ArgumentModelSerializer(ModelSerializerDrf):
    """Serializer for arguments."""

    premises = _PropositionModelSerializer(many=True, source='premises.all')

    class Meta(ModelSerializerDrf.Meta):
        model = Argument
        fields = ModelSerializerDrf.Meta.fields + ['explanation', 'premises']


class PropositionModelSerializer(_PropositionModelSerializer):
    """Serializer for propositions."""

    arguments = ArgumentModelSerializer(many=True, source='arguments.all')

    class Meta(_PropositionModelSerializer.Meta):
        model = Proposition
        fields = _PropositionModelSerializer.Meta.fields + ['arguments']


class OccurrenceModelSerializer(PropositionModelSerializer):
    """Serializer for occurrences."""

    def get_model(self, instance) -> str:
        """Return the model name of the instance."""
        return 'propositions.occurrence'

    class Meta(PropositionModelSerializer.Meta):
        model = Occurrence
        fields = PropositionModelSerializer.Meta.fields + ['postscript']
