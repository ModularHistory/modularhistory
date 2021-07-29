from typing import Type, Union

from django.db import models
from django.utils.translation import ugettext_lazy as _

from core.fields.custom_m2m_field import CustomManyToManyField


class AbstractScmItem(models.Model):
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

    def __str__(self) -> str:
        return f'{self.title} (created by {self.creator}): {self.url}'


class ContentContribution(models.Model):
    """A content contribution."""

    contributor = models.ForeignKey(
        to='users.User',
        related_name='content_contributions',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )
    branch = models.ForeignKey(
        to='cms.Branch',
        related_name='contributions',
        on_delete=models.PROTECT,
    )

    def __str__(self) -> str:
        return f'{self.branch} <-- {self.contributor}'


class Branch(AbstractScmItem):
    """A branch in ModularHistory's content repo."""

    contributors = models.ManyToManyField(
        to='users.User',
        through=ContentContribution,
        related_name='branches_contributed_to',
        blank=True,
    )
    source = models.ForeignKey(
        to='self',
        related_name='branches',
        on_delete=models.PROTECT,
        null=True,
        blank=True,
    )


class PullRequest(AbstractScmItem):
    """A pull request in ModularHistory's content repo."""


class Issue(AbstractScmItem):
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
