from typing import Type, Union

from django.db import models
from django.utils.translation import ugettext_lazy as _

from core.fields.custom_m2m_field import CustomManyToManyField


class ScmItem(models.Model):
    """Base model for pull requests and issues."""

    creator = models.ForeignKey(
        to='users.User',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )
    title = models.CharField(verbose_name=_('title'), max_length=200)
    url = models.URLField(verbose_name=_('URL'))

    class Meta:
        abstract = True


class PullRequest(ScmItem):
    """A pull request in ModularHistory's content repo."""


class Issue(ScmItem):
    """An issue in ModularHistory's content repo."""


class AbstractModification(models.Model):
    """Base for m2m relationships with PullRequest."""

    pull_request = models.ForeignKey(to=PullRequest, on_delete=models.CASCADE)

    class Meta:
        abstract = True


class PullRequestsField(CustomManyToManyField):
    """Custom field for m2m relationship with pull requests."""

    target_model = 'cms.PullRequest'
    through_model_base = AbstractModification

    def __init__(self, through: Union[Type[AbstractModification], str], **kwargs):
        """Construct the field."""
        kwargs['through'] = through
        kwargs['verbose_name'] = _('pull requests')
        super().__init__(**kwargs)
