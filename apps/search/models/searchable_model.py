"""Base classes for models that appear in ModularHistory search results."""


from django.db import models


class SearchableModel(models.Model):
    """Abstract base model for models of which instances should be searchable."""

    # https://docs.djangoproject.com/en/dev/ref/models/options/#model-meta-options
    class Meta:
        abstract = True
