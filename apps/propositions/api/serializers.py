from apps.propositions.models import Argument, Occurrence, Proposition
from core.models.model import DrfModelSerializer
from core.models.module import DrfModuleSerializer


class _PropositionDrfSerializer(DrfModuleSerializer):
    """Serializer for propositions."""

    def get_model(self, instance) -> str:
        """Return the model name of serialized propositions."""
        return 'propositions.proposition'

    class Meta(DrfModuleSerializer.Meta):
        model = Proposition
        fields = DrfModuleSerializer.Meta.fields + [
            'summary',
            'elaboration',
            'truncated_elaboration',
            'certainty',
            'date_string',
            'tags_html',
            'cached_citations',
            'primary_image',
            'cached_images',
        ]
        read_only_fields = ['truncated_elaboration']
        extra_kwargs = {'certainty': {'required': False}}


class ArgumentDrfSerializer(DrfModelSerializer):
    """Serializer for arguments."""

    premises = _PropositionDrfSerializer(many=True, source='premises.all')

    class Meta(DrfModelSerializer.Meta):
        model = Argument
        fields = DrfModelSerializer.Meta.fields + ['explanation', 'premises']


class PropositionDrfSerializer(_PropositionDrfSerializer):
    """Serializer for propositions."""

    arguments = ArgumentDrfSerializer(many=True, source='arguments.all')

    class Meta(_PropositionDrfSerializer.Meta):
        model = Proposition
        fields = _PropositionDrfSerializer.Meta.fields + ['arguments']


class OccurrenceDrfSerializer(PropositionDrfSerializer):
    """Serializer for occurrences."""

    def get_model(self, instance) -> str:
        """Return the model name of the instance."""
        return 'propositions.occurrence'

    class Meta(PropositionDrfSerializer.Meta):
        model = Occurrence
        fields = PropositionDrfSerializer.Meta.fields + ['postscript']
