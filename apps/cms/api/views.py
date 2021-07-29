from typing import Union

from django.http import JsonResponse
from github import Github
from rest_framework.decorators import api_view
from rest_framework.generics import CreateAPIView
from rest_framework.request import Request
from rest_framework.response import Response

from apps.cms.api.serializers import BranchSerializer
from apps.cms.models import Branch


class CreateBranch(CreateAPIView):
    """View for creating a branch in the content repo."""

    queryset = Branch.objects.all()
    serializer_class = BranchSerializer

    def post(
        self,
        request: Request,
        target_branch: str,
        source_branch: str = 'main',
    ) -> Response:
        access_token = request.user.github_access_token
        client = Github(access_token)
        repo = client.get_repo('ModularHistory/modularhistory')
        source_branch = repo.get_branch(source_branch)
        repo.create_git_ref(ref=f'refs/heads/{target_branch}/', sha=source_branch.commit.sha)
        target_branch = repo.get_branch(target_branch)
        return super().post(self, request)

    def create(self, request: Request) -> Response:
        return super().create(request)


@api_view(['GET'])
def cms(request: Request, directory: str, id: Union[int, str]):
    """Ensure the CSRF cookie is set correctly."""
    access_token = request.user.github_access_token
    if access_token:
        try:
            client = Github(access_token)
            repo = client.get_repo('ModularHistory/modularhistory')
            contents = repo.get_contents(f'{directory}/{id}.toml')
            pull_requests = repo.get_pulls()
            return JsonResponse({'contents': contents})
        except AttributeError:
            pass
    return JsonResponse({})
