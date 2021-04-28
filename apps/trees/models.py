"""Based on https://github.com/peopledoc/django-ltree-demo."""

import logging
import re

import regex
from django.core.validators import RegexValidator
from django.db import models
from django.utils.translation import ugettext_lazy as _

from apps.trees.fields import LtreeField
from core.models.model import Model


class TreeModel(Model):
    """Implements Postgres ltree for self-referencing hierarchy."""

    parent = models.ForeignKey(
        to='self',
        null=True,
        blank=True,
        # Direct children can be accessed via the `children` property.
        related_name='children',
        on_delete=models.CASCADE,
        verbose_name=_('parent'),
    )
    name = models.TextField(verbose_name=_('name'))
    # The `key` field is a unique identifier for the node.
    # It is derived from the `name` field.
    key = models.CharField(
        max_length=32,
        unique=True,
        null=True,
        validators=[RegexValidator(regex=r'\w*')],
        verbose_name=_('key'),
    )
    # The `path` field represents the path from the root to the node,
    # where each node is represented by its key.
    path = LtreeField()

    class Meta:
        """Meta options for DatedModel."""

        # https://docs.djangoproject.com/en/3.1/ref/models/options/#model-meta-options
        abstract = True

    def save(self, *args, **kwargs):
        """Save the model instance to the database."""
        # Set the key.
        key = self.get_key()
        if not self.key:
            self.key = key
        elif self.key != key:
            if self.__class__.objects.filter(key=key).exists():
                logging.info(f'A topic with key={key} already exists.')
            else:
                self.key = key
        # If there is no path, set it equal to the key, making the topic a top-level
        # (parentless) topic.
        if not self.path:
            self.path = self.key
        # If the final (or only) element of the path does not match the key,
        # update the path to use the key as its final (or only) element.
        elif self.path.split('.')[-1] != self.key:
            self.path = re.sub(r'(.*(?:^|\.)).+$', rf'\1{self.key}', self.path)
        return super().save(*args, **kwargs)

    def get_key(self) -> str:
        """Set the model instance's key value based on its name."""
        name: str = self.name
        key = name.lower().replace('&', 'and')
        # Replace spaces and any kind of hyphen/dash with an underscore.
        key = regex.sub(r'(?:\ |\p{Pd})', '_', key)
        # Remove any other non-alphanumeric characters.
        return regex.sub(r'\W', '', key)
