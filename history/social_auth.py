from tempfile import NamedTemporaryFile
from urllib.request import urlopen

from django.core.files import File
from social_core.backends.facebook import FacebookOAuth2
from social_core.backends.google import GoogleOAuth2
from social_core.backends.twitter import TwitterOAuth


def get_user_avatar(backend, response, user, *args, **kwargs):
    print('Attempting to retrieve user profile image...')
    url = None
    try:
        if backend.name == 'facebook' or isinstance(backend, FacebookOAuth2):
            url = f'http://graph.facebook.com/{response["id"]}/picture?type=large'
        elif backend.name == 'twitter' or isinstance(backend, TwitterOAuth):
            url = response.get('profile_image_url', '').replace('_normal', '')
        elif backend.name.startswith('google') or isinstance(backend, GoogleOAuth2):
            if response.get('image') and response['image'].get('url'):
                url = response['image'].get('url')
        if url:
            if not user.avatar:  # TODO: also check if image has been updated
                print(f'{user} has no profile image.')
                img_temp = NamedTemporaryFile(delete=True)
                img_temp.write(urlopen(url).read())
                img_temp.flush()
                user.avatar.save(f'{user.pk}', File(img_temp))
        else:
            print(f'Unable to determine profile picture URL for {user}')
    except Exception as e:
        print(f'>>> {type(e)} in get_user_avatar: {e}')
        raise
