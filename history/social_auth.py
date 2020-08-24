from tempfile import NamedTemporaryFile
from urllib.request import urlopen

from django.core.files import File
from social_core.backends.facebook import FacebookOAuth2
from social_core.backends.google import GoogleOAuth2
from social_core.backends.twitter import TwitterOAuth
from social_core.backends.github import GithubOAuth2

FACEBOOK = 'facebook'
TWITTER = 'twitter'
GOOGLE = 'google'


def get_user_avatar(backend, response, user, *args, **kwargs):
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
