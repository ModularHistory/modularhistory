from tempfile import NamedTemporaryFile
from typing import Dict, Optional, Union
from urllib.request import urlopen

import requests
from django.core.files import File
from social_core.backends.facebook import FacebookOAuth2
from social_core.backends.github import GithubOAuth2
from social_core.backends.google import GoogleOAuth2
from social_core.backends.oauth import BaseOAuth1, BaseOAuth2
from social_core.backends.twitter import TwitterOAuth

from account.models import User

FACEBOOK = 'facebook'
TWITTER = 'twitter'
GOOGLE = 'google'
GITHUB = 'github'

Backend = Union[BaseOAuth1, BaseOAuth2]


def get_user_email(backend: Backend, response: Dict, **kwargs):
    """
    Get the user's email address if it has not already been retrieved.

    In most cases, the backend should automatically supply the user's email address.
    If it doesn't, try to get the email address through the backend's API.
    """
    details = kwargs.get('details')
    if details and details.get('email', None):
        if backend.name == 'github' or isinstance(backend, GithubOAuth2):
            access_token = response.get('access_token', None)
            email = None
            if access_token:
                request_url = 'https://api.github.com/user/emails'
                params = {'state': 'open'}
                headers = {'Authorization': f'token {access_token}'}
                response = requests.get(request_url, headers=headers, params=params).json()
                try:
                    for item in response:
                        if item.get('primary', False) and item.get('verified', False):
                            email = item.get('email', None)
                except Exception as e:
                    print(f'Error processing response from {request_url}: {type(e)}: {e}')
            if email:
                details['email'] = email
                return {'details': details}


def get_user_avatar(backend: Backend, response: Dict, user: User, *args, **kwargs):
    """Retrieve and save the user's profile picture from the supplied auth backend."""
    try:
        url = _get_avatar_url_from_backend(backend, response, user, **kwargs)
        # Update the user's avatar
        if url:
            _update_user_avatar(user, url)
    except Exception as e:
        print(f'>>> {type(e)} in get_user_avatar: {e}')
        raise


def _get_avatar_url_from_backend(backend: Backend, response: Dict, user: User, **kwargs) -> Optional[str]:
    """Attempts to retrieve a URL for the user's current avatar in a social auth backend."""
    url = None
    if backend.name == 'facebook' or isinstance(backend, FacebookOAuth2):
        url = f'http://graph.facebook.com/{response["id"]}/picture?type=large&breaking_change=profile_picture'
    elif backend.name == 'twitter' or isinstance(backend, TwitterOAuth):
        url = response.get('profile_image_url', '').replace('_normal', '')
    elif backend.name.startswith('google') or isinstance(backend, GoogleOAuth2):
        if response.get('image') and response['image'].get('url'):
            url = response['image'].get('url')
    elif backend.name == 'github' or isinstance(backend, GithubOAuth2):
        details = kwargs.get('details', {})
        username = kwargs.get('username', details.get('username', user.email.split('@')[0]))
        url = f'https://github.com/{username}.png'
    elif response.get('picture'):
        url = response['picture']
    else:
        print(f'Unable to determine profile image URL for unhandled auth backend: {backend.name}')
    return url


def _update_user_avatar(user: User, url: str):
    """Update the user's avatar with the image located at the given URL."""
    if user.avatar:
        print(f'{user} already has an avatar: {user.avatar}')
        # TODO: check if image has been updated
    else:
        print(f'{user} has no profile image.')
        img_temp = NamedTemporaryFile(delete=True)
        # TODO: Use requests instead of urllib?
        img_temp.write(urlopen(url).read())  # noqa: S310
        img_temp.flush()
        user.avatar.save(f'{user.pk}', File(img_temp))
