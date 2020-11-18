import logging
from typing import Dict, Optional

from social_core.backends.facebook import FacebookOAuth2
from social_core.backends.github import GithubOAuth2
from social_core.backends.google import GoogleOAuth2
from social_core.backends.twitter import TwitterOAuth

from account.models import User
from account.social_auth.auth_data import AuthBackend, auth_data_interfaces

FACEBOOK = 'facebook'
TWITTER = 'twitter'
GOOGLE = 'google'
GITHUB = 'github'


def get_user_avatar(backend: AuthBackend, response: Dict, user: User, *args, **kwargs):
    """Retrieve and save the user's profile picture from the supplied auth backend."""
    try:
        url = _get_avatar_url_from_backend(backend, response, user, **kwargs)
        # Update the user's avatar
        if url:
            user.update_avatar(url)
    except Exception as error:
        logging.error(f'{type(error)} in get_user_avatar: {error}')
        raise


def _get_avatar_url_from_backend(
    backend: AuthBackend, response: Dict, user: User, **kwargs
) -> Optional[str]:
    """Attempt to retrieve a URL for the user's avatar in a social auth backend."""
    url = None
    name = backend.name
    backends = (
        ('facebook', FacebookOAuth2),
        ('twitter', TwitterOAuth),
        ('github', GithubOAuth2),
        ('google', GoogleOAuth2),
    )
    for backend_name, backend_type in backends:
        if name == backend_name or isinstance(backend, backend_type):
            auth_data_interface_cls = auth_data_interfaces.get(backend_name)
            auth_data_interface = auth_data_interface_cls(response, user, **kwargs)
            url = auth_data_interface.get_profile_pic_url()
            break
    else:
        if response.get('picture'):
            url = response['picture']
        else:
            logging.error(
                f'Unable to determine profile image URL for unhandled auth backend: {name}'
            )
    return url
