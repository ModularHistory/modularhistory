from typing import TYPE_CHECKING, Type, Union

from django.db import models
from django.utils.translation import ugettext_lazy as _

from core.fields.custom_m2m_field import CustomManyToManyField

if TYPE_CHECKING:
    from github.Branch import Branch as GithubBranch
    from github.PullRequest import PullRequest as GithubPullRequest
    from github.Repository import Repository as GithubRepository


class AbstractScmItem(models.Model):
    """Base model for SCM objects like pull requests and issues."""

    creator = models.ForeignKey(
        to='users.User',
        on_delete=models.SET_NULL,
        related_name='%(app_label)s_%(class)s_set',
        null=True,
        blank=True,
    )
    url = models.URLField(verbose_name=_('URL'))

    class Meta:
        abstract = True

    def __str__(self) -> str:
        return f'{self.title} (created by {self.creator}): {self.url}'


class NumberedScmItem(AbstractScmItem):
    """Base model for pull requests and issues."""

    number = models.PositiveIntegerField(db_index=True)
    title = models.CharField(verbose_name=_('title'), max_length=200)

    class Meta:
        abstract = True


class Issue(NumberedScmItem):
    """An issue in the content repo."""


class Commit(AbstractScmItem):
    """A commit in the content repo."""

    committer = models.ForeignKey(
        to='users.User',
        related_name='commits',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )
    sha = models.CharField(max_length=100)
    message = models.TextField()
    parents = models.ManyToManyField(
        to='self',
        symmetrical=False,
        related_name='children',
        blank=True,
    )

    def __str__(self) -> str:
        return f'Commit {self.sha}: "{self.message}" (by {self.creator})'


class Branch(AbstractScmItem):
    """A branch in the content repo."""

    name = models.CharField(
        verbose_name=_('name'),
        max_length=100,
        unique=True,
    )
    source = models.ForeignKey(
        to='self',
        related_name='branches',
        on_delete=models.PROTECT,
        null=True,
        blank=True,
    )
    commit = models.ForeignKey(
        to=Commit,
        on_delete=models.PROTECT,
        null=True,
        blank=True,
    )

    def __str__(self) -> str:
        return f'Branch "{self.name}" (created by {self.creator})'

    @classmethod
    def create_from_github(cls, pr: 'GithubBranch') -> 'Branch':
        pass


class PullRequest(NumberedScmItem):
    """A pull request in the content repo."""

    commits = models.ManyToManyField(to=Commit, related_name='pull_requests')
    source_branch = models.ForeignKey(to=Branch, on_delete=models.PROTECT)
    target_branch = models.ForeignKey(
        to=Branch,
        on_delete=models.PROTECT,
        related_name='pull_requests',
    )
    issues_resolved = models.ManyToManyField(
        to=Issue,
        related_name='pull_requests',
        blank=True,
    )

    @classmethod
    def create_from_github(cls, pr: 'GithubPullRequest') -> 'PullRequest':
        """Create a pull request instance from its corresponding GitHub pull request."""
        return cls.objects.create(
            number=pr.number,
            title=pr.title,
            url=pr.url,
            source_branch=Branch.objects.get_or_create(name=pr.head.ref)[0],
            target_branch=Branch.objects.get_or_create(name=pr.base.ref)[0],
        )


class Review(models.Model):
    """A review of a pull request in the content repo."""

    pull_request = models.ForeignKey(
        to=PullRequest,
        related_name='reviews',
        on_delete=models.CASCADE,
    )
    reviewer = models.ForeignKey(
        to='users.User',
        related_name='cms_reviews',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )


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
