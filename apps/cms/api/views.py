from django.conf import settings
from github import Github
from rest_framework import permissions
from rest_framework.generics import CreateAPIView, ListAPIView, RetrieveUpdateAPIView
from rest_framework.request import Request
from rest_framework.response import Response

from apps.cms import models
from apps.cms.api.serializers import BranchSerializer, IssueSerializer, PullRequestSerializer
from apps.cms.models import Branch, Issue, PullRequest
from core.utils import github


class BranchCreationView(CreateAPIView):
    """View for creating a branch in the content repo."""

    queryset = Branch.objects.all()
    serializer_class = BranchSerializer
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request: Request, *args, **kwargs) -> Response:
        """Respond to a POST request."""
        access_token = request.user.github_access_token
        client = Github(access_token)
        branch = github.create_branch(
            client,
            source_branch_name=request.data['source_branch'],
            target_branch_name=request.data['target_branch'],
        )
        # TODO: confirm all is well with the new branch before saving?
        return super().post(self, request, *args, **kwargs)

    def create(self, request: Request) -> Response:
        """Create and save the new branch."""
        return super().create(request)


class IssueAPIView:

    queryset = Issue.objects.all()
    serializer_class = IssueSerializer
    permission_classes = [permissions.IsAuthenticated]
    lookup_field = 'number'


class IssueCreationView(IssueAPIView, CreateAPIView):
    """View for creating an issue in the content repo."""

    def post(self, request: Request, *args, **kwargs) -> Response:
        """Respond to a POST request."""
        # access_token = request.user.github_access_token
        # client = Github(access_token)
        # repo = client.get_repo(settings.CONTENT_REPO)
        # issues = repo.get_issues()
        return super().post(self, request, *args, **kwargs)

    def create(self, request: Request) -> Response:
        """Create and save the new branch."""
        return super().create(request)


class IssueListView(IssueAPIView, ListAPIView):
    """View for listing issues."""


class IssueView(IssueAPIView, RetrieveUpdateAPIView):
    """View for displaying and/or updating an issue."""


class IssueView(IssueAPIView, RetrieveUpdateAPIView):
    """View for retrieving and/or updating an issue in the content repo."""

    def retrieve(self, request: Request, number: int) -> Response:
        """Retrieve the pull request."""
        access_token = request.user.github_access_token
        client = Github(access_token)
        repo = client.get_repo(settings.CONTENT_REPO)
        issue = repo.get_issue(number)
        if models.Issue.objects.filter(number=number).exists():
            instance = models.Issue.objects.get(number=number)
        else:
            instance = models.Issue.create_from_github(issue)
        serializer = self.get_serializer(instance)
        return Response(serializer.data)


class PullRequestAPIView:

    queryset = PullRequest.objects.all()
    serializer_class = PullRequestSerializer
    permission_classes = [permissions.IsAuthenticated]
    lookup_field = 'number'


class PullRequestCreationView(PullRequestAPIView, CreateAPIView):
    """View for creating a pull request in the content repo."""

    def post(self, request: Request, *args, **kwargs) -> Response:
        """Respond to a POST request."""
        access_token = request.user.github_access_token
        client = Github(access_token)
        pull_request = github.create_pull_request(
            client,
            title=request.data['title'],
            body=request.data['body'],
            source_branch_name=request.data['source_branch'],
            target_branch_name=request.data.get('target_branch', default='main'),
        )
        return super().post(self, request, *args, **kwargs)

    def create(self, request: Request) -> Response:
        """Create and save the new branch."""
        return super().create(request)


class PullRequestListView(PullRequestAPIView, ListAPIView):
    """View for listing pull requests."""


class PullRequestView(PullRequestAPIView, RetrieveUpdateAPIView):
    """View for retrieving and/or updating a pull request in the content repo."""

    def retrieve(self, request: Request, number: int) -> Response:
        """Retrieve the pull request."""
        access_token = request.user.github_access_token
        client = Github(access_token)
        repo = client.get_repo(settings.CONTENT_REPO)
        pull_request = repo.get_pull(number)

        if models.PullRequest.objects.filter(number=number).exists():
            instance = models.PullRequest.objects.get(number=number)
        else:
            instance = models.PullRequest.create_from_github(pull_request)
        serializer = self.get_serializer(instance)
        return Response(serializer.data)
