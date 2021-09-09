from core.models.model import ExtendedModel


class SearchableModel(ExtendedModel):
    """Abstract base model for models of which instances should be searchable."""

    # https://docs.djangoproject.com/en/dev/ref/models/options/#model-meta-options
    class Meta:
        abstract = True
