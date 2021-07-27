from typing import Union

from django.http import JsonResponse
from github import Github
from rest_framework.decorators import api_view
from rest_framework.request import Request


# @api_view(['GET'])
# def cms(request: Request, directory: str, id: Union[int, str]):
#     """Ensure the CSRF cookie is set correctly."""
#     access_token = request.user.github_access_token
#     if access_token:
#         try:
#             client = Github(access_token)
#             repo = client.get_repo('ModularHistory/modularhistory')
#             contents = repo.get_contents(f'{directory}/{id}.toml')
#             pull_requests = repo.get_pulls()
#             return JsonResponse({'contents': contents})
#         except AttributeError:
#             pass
#     return JsonResponse({})
