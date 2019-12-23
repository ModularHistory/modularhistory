from account.forms import ChangeForm
from account.models import User
from django import forms
from django.conf import settings
from django.contrib import messages
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.decorators import permission_required, login_required
from django.contrib.auth.forms import AdminPasswordChangeForm, PasswordChangeForm
from django.forms.models import model_to_dict
from django.http import HttpResponse, HttpResponseRedirect, Http404
from django.shortcuts import get_object_or_404
from django.utils import timezone
from django_mako_plus import view_function, jscontext
from social_django.models import UserSocialAuth

import datetime


@view_function
@login_required(login_url='/account/login')
def process_request(request):
    """User Details"""
    user = request.user
    try:
        google_login = user.social_auth.get(provider='google_oauth2')
    except UserSocialAuth.DoesNotExist:
        google_login = None
    # try:
    #     twitter_login = user.social_auth.get(provider='twitter')
    # except UserSocialAuth.DoesNotExist:
    #     twitter_login = None
    try:
        facebook_login = user.social_auth.get(provider='facebook')
    except UserSocialAuth.DoesNotExist:
        facebook_login = None

    can_disconnect = (user.social_auth.count() > 1 or user.has_usable_password())

    if user.avatar is not None:
        profile_image = user.avatar
    elif user.gender == 'F':
        profile_image = 'nobody_f.jpg'
    else:
        profile_image = 'nobody_m.jpg'

    participant = None
    if len(user.event_participations.all()) > 0:
        participant = user

    context = {
        'user': user,
        'name': user.get_full_name(),
        'email': user.email,
        'profile_image': profile_image,
        'participant': participant,
        'google_login': google_login,
        # 'twitter_login': twitter_login,
        'facebook_login': facebook_login,
        'can_disconnect': can_disconnect,
    }
    return request.dmp.render('settings.html', context)


@view_function
@login_required(login_url='/account/login')
def password(request):
    if request.user.has_usable_password():
        PasswordForm = PasswordChangeForm
    else:
        PasswordForm = AdminPasswordChangeForm
    if request.method == 'POST':
        form = PasswordForm(request.user, request.POST)
        if form.is_valid():
            form.save()
            update_session_auth_hash(request, form.user)
            messages.success(request, 'Your password was successfully updated!')
            redirect_url = '/account/settings/'
            if form.user.force_password_change:
                form.user.force_password_change = False
                redirect_url = '/home/'
            form.user.save()
            # authenticate(username=user.username, password=form.cleaned_data.get('password1'))
            # login(request, form.user)
            return HttpResponse("""
                <p class="text-center">Successfully changed password. Redirecting...</p>
                <script>
                    function redirect() {
                        window.location.href = '%s';
                    }
                    window.setTimeout(redirect, 2000);
                </script>
            """ % redirect_url)
        else:
            messages.error(request, 'Please correct the error below.')
    else:
        form = PasswordForm(request.user)
    context = {
        'form': form,
    }
    return request.dmp.render('password.html', context)
