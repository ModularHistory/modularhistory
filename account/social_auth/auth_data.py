import logging
from typing import Dict, Optional, Union

import requests
from social_core.backends.oauth import BaseOAuth1, BaseOAuth2

from account.models import User

AuthBackend = Union[BaseOAuth1, BaseOAuth2]


class AuthData:
    """Interface for data provided by a social auth backend."""

    def __init__(self, response: Dict, user: Optional[User] = None, **kwargs):
        """Construct the auth data interface."""
        self.response = response
        self.user = user
        self.kwargs = kwargs

    def get_email(self) -> Optional[str]:
        """Return the user's email address from the social auth data."""
        raise NotImplementedError

    def get_profile_pic_url(self) -> Optional[str]:
        """Return the URL for the user's profile picture."""
        raise NotImplementedError


class FacebookAuthData(AuthData):
    """Interface for data provided by Facebook social auth."""

    def get_email(self) -> Optional[str]:
        """Return the user's email address used by Facebook."""
        raise NotImplementedError

    def get_profile_pic_url(self):
        """Return the URL for the user's Facebook profile picture."""
        return (
            f'http://graph.facebook.com/{self.response["id"]}/picture'
            '?type=large&breaking_change=profile_picture'
        )


class GitHubAuthData(AuthData):
    """Interface for data provided by GitHub social auth."""

    def get_email(self) -> Optional[str]:
        """Return the user's email address used by GitHub."""
        access_token = self.response.get('access_token', None)
        email = None
        if access_token:
            request_url = 'https://api.github.com/user/emails'
            request_params = {'state': 'open'}
            request_headers = {'Authorization': f'token {access_token}'}
            response = requests.get(
                request_url, headers=request_headers, params=request_params
            ).json()
            try:
                for email_item in response:
                    email_item_is_usable = email_item.get(
                        'primary', False
                    ) and email_item.get('verified', False)
                    if email_item_is_usable:
                        email = email_item.get('email', None)
            except Exception as error:
                logging.error(
                    f'Error processing response from {request_url}: '
                    f'{type(error)}: {error}'
                )
        return email

    def get_profile_pic_url(self):
        """Return the URL for the user's GitHub profile picture."""
        details = self.kwargs.get('details', {})
        username = self.kwargs.get(
            'username', details.get('username', self.user.email.split('@')[0])
        )
        return f'https://github.com/{username}.png'


class GoogleAuthData(AuthData):
    """Interface for data provided by Google social auth."""

    def get_email(self) -> Optional[str]:
        """Return the user's email address used by Google."""
        raise NotImplementedError

    def get_profile_pic_url(self):
        """Return the URL for the user's Google profile picture."""
        image = self.response.get('image')
        if image:
            return image.get('url')


class TwitterAuthData(AuthData):
    """Interface for data provided by Twitter social auth."""

    def get_email(self) -> Optional[str]:
        """Return the user's email address used by Twitter."""
        raise NotImplementedError

    def get_profile_pic_url(self):
        """Return the URL for the user's Twitter profile picture."""
        return self.response.get('profile_image_url', '').replace('_normal', '')


auth_data_interfaces = {
    'facebook': FacebookAuthData,
    'github': GitHubAuthData,
    'google': GoogleAuthData,
    'twitter': TwitterAuthData,
}
