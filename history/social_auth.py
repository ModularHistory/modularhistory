from pprint import pprint
from tempfile import NamedTemporaryFile
from typing import Dict, Union
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
    If a backend does not automatically supply the user's email address,
    try to get the email address through the backend's API.
    """
    details = kwargs.get('details')
    if details and details.get('email', None):
        if backend.name == 'github' or isinstance(backend, GithubOAuth2):
            access_token = response.get('access_token', None)
            email = None
            if access_token:
                request_url = f'https://api.github.com/user/emails'
                params = {"state": "open"}
                headers = {'Authorization': f'token {access_token}'}
                response = requests.get(request_url, headers=headers, params=params).json()
                if isinstance(response, list):
                    for item in response:
                        if item.get('primary', False) and item.get('verified', False):
                            email = item.get('email', None)
            if email:
                details['email'] = email
                return {'details': details}


def get_user_avatar(backend: Backend, response: Dict, user: User, *args, **kwargs):
    """Retrieve and save the user's profile picture from the supplied auth backend."""
    url = None
    try:
        # Determine the profile image URL
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

        # Update the user's avatar
        if url:
            if not user.avatar:
                print(f'{user} has no profile image.')
                img_temp = NamedTemporaryFile(delete=True)
                img_temp.write(urlopen(url).read())
                img_temp.flush()
                user.avatar.save(f'{user.pk}', File(img_temp))
            else:
                print(f'{user} already has an avatar: {user.avatar}')
                # TODO: check if image has been updated
    except Exception as e:
        print(f'>>> {type(e)} in get_user_avatar: {e}')
        raise
