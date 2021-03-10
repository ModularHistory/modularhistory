from typing import Dict

from social_core.backends.github import GithubOAuth2

from apps.account.social_auth.auth_data import AuthBackend, auth_data_interfaces


def get_user_email(backend: AuthBackend, response: Dict, **kwargs):
    """
    Get the user's email address if it has not already been retrieved.

    In most cases, the backend should automatically supply the user's email address.
    If it doesn't, try to get the email address through the backend's API.
    """
    details = kwargs.get('details')
    if details and details.get('email', None):
        if backend.name == 'github' or isinstance(backend, GithubOAuth2):
            auth_data_interface = auth_data_interfaces['github'](response, **kwargs)
            email = auth_data_interface.get_email()
            if email:
                details['email'] = email
                return {'details': details}
