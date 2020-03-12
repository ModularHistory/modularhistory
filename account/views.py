from django.contrib.auth import authenticate, login
from django.contrib.auth import views as auth_views
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from django.views.generic import View
from social_django.models import UserSocialAuth

from .forms import LoginForm, RegistrationForm


class LoginView(auth_views.LoginView):
    form_class = LoginForm
    template_name = 'account/login.html'


class LogoutView(auth_views.LogoutView):
    pass


class PasswordChangeView(auth_views.PasswordChangeView):
    template_name = 'account/password_change_form.html'
    success_url = reverse_lazy('account:password_change_done')


class PasswordChangeDoneView(auth_views.PasswordChangeDoneView):
    template_name = 'account/password_change_done.html'


class PasswordResetView(auth_views.PasswordResetView):
    template_name = 'account/password_reset_form.html'
    email_template_name = 'account/password_reset_email.html'
    success_url = reverse_lazy('account:password_reset_done')


class PasswordResetDoneView(auth_views.PasswordResetDoneView):
    template_name = 'account/password_reset_done.html'


class PasswordResetCompleteView(auth_views.PasswordResetCompleteView):
    template_name = 'account/password_reset_complete.html'


class RegisterView(View):
    def get(self, request):
        form = RegistrationForm()
        context = {'form': form}
        return render(request, 'account/register.html', context)

    def post(self, request):
        form = RegistrationForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get('username')
            raw_password = form.cleaned_data.get('password1')
            user = authenticate(username=username, password=raw_password)
            login(request, user)
            return redirect('home')


class ProfileView(LoginRequiredMixin, View):
    """Profile view"""
    def get(self, request):
        user = request.user
        context = {
            'user': user,
            'name': user.get_full_name(),
            'email': user.email,
            'profile_image_url': user.avatar.url if user.avatar else None,
        }
        return render(request, 'account/profile.html', context)


class SettingsView(LoginRequiredMixin, View):
    """Account settings view"""
    def get(self, request):
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

        context = {
            'user': user,
            'name': user.get_full_name(),
            'email': user.email,
            'profile_image': profile_image,
            'google_login': google_login,
            # 'twitter_login': twitter_login,
            'facebook_login': facebook_login,
            'can_disconnect': can_disconnect,
        }
        return render(request, 'account/settings.html', context)


# from account.forms import ChangeForm, PictureForm

# @view_function
# @login_required(login_url='/account/login')
# def process_request(request):
#     """User Details"""
#     user = request.user
#     if user.avatar:
#         profile_image_url = user.avatar.url
#     elif user.gender == 'F':
#         profile_image_url = '%saccount/media/nobody_f.jpg' % settings.STATIC_URL
#     else:
#         profile_image_url = '%saccount/media/nobody_m.jpg' % settings.STATIC_URL
#     context = {
#         'user': user,
#         'name': user.get_full_name(),
#         'email': user.email,
#         'profile_image_url': profile_image_url,
#     }
#     return request.dmp.render('profile.html', context)


# @view_function
# @login_required(login_url='/account/login')
# def edit(request):
#     """Page for editing user profile"""
#     # process the form
#     form = ChangeForm(request, instance=request.user)
#     if form.is_valid():
#         u = request.user
#         if 'picture' in request.FILES:
#             u.avatar = form.cleaned_data.get('picture')
#         u.username = form.cleaned_data.get('username')
#         u.first_name = form.cleaned_data.get('first_name')
#         u.last_name = form.cleaned_data.get('last_name')
#         u.email = form.cleaned_data.get('email')
#         u.date_of_birth = form.cleaned_data.get('date_of_birth')
#         u.address = form.cleaned_data.get('address')
#         u.address2 = form.cleaned_data.get('address2')
#         u.city = form.cleaned_data.get('city')
#         u.state = form.cleaned_data.get('state')
#         u.zip_code= form.cleaned_data.get('zip')
#         u.phone_number = form.cleaned_data.get('phone_number')
#         weight = form.cleaned_data.get('weight')
#         if weight:
#             u.weight = form.cleaned_data.get('weight')
#             u.update_registered_weight(weight)
#         u.belt = form.cleaned_data.get('belt')
#         u.stripes = form.cleaned_data.get('stripes')
#         u.save()
#         for ep in u.event_participations.filter(event__datetime__gte=datetime.datetime.today()):
#             ep.belt = form.cleaned_data.get('belt')
#             ep.stripes = form.cleaned_data.get('stripes')
#             ep.save()
#         return HttpResponseRedirect('/account/profile/')
#     context = {
#         'form': form,
#     }
#     return request.dmp.render('profile.edit.html', context)
#
#
# @view_function
# @login_required(login_url='/account/login')
# def picture(request):
#     form = PictureForm(request, initial={'picture': request.user.avatar, })
#     if form.is_valid():
#         u = request.user
#         u.avatar = form.cleaned_data.get('picture')
#         u.save()
#         redirect_url = '/account/profile/'
#         return HttpResponse("""
#             <p class="text-center" style="display: none">
#                 Uploaded successfully.  Redirecting...
#             </p>
#             <script>
#                 window.location.href = '%s';
#             </script>
#         """ % redirect_url)
#     context = {
#         'form': form,
#     }
#     return request.dmp.render('/home/templates/form.html', context)

# from account.forms import ChangeForm
# from account.models import User
# from django import forms
# from django.conf import settings
# from django.contrib import messages
# from django.contrib.auth import update_session_auth_hash
# from django.contrib.auth.decorators import permission_required, login_required
# from django.contrib.auth.forms import AdminPasswordChangeForm, PasswordChangeForm
# from django.forms.models import model_to_dict
# from django.http import HttpResponse, HttpResponseRedirect, Http404
# from django.shortcuts import get_object_or_404
# from django.utils import timezone
# from social_django.models import UserSocialAuth
#
# import datetime
#
#
#
#
# @view_function
# @login_required(login_url='/account/login')
# def password(request):
#     if request.user.has_usable_password():
#         PasswordForm = PasswordChangeForm
#     else:
#         PasswordForm = AdminPasswordChangeForm
#     if request.method == 'POST':
#         form = PasswordForm(request.user, request.POST)
#         if form.is_valid():
#             form.save()
#             update_session_auth_hash(request, form.user)
#             messages.success(request, 'Your password was successfully updated!')
#             redirect_url = '/account/settings/'
#             if form.user.force_password_change:
#                 form.user.force_password_change = False
#                 redirect_url = '/home/'
#             form.user.save()
#             # authenticate(username=user.username, password=form.cleaned_data.get('password1'))
#             # login(request, form.user)
#             return HttpResponse("""
#                 <p class="text-center">Successfully changed password. Redirecting...</p>
#                 <script>
#                     function redirect() {
#                         window.location.href = '%s';
#                     }
#                     window.setTimeout(redirect, 2000);
#                 </script>
#             """ % redirect_url)
#         else:
#             messages.error(request, 'Please correct the error below.')
#     else:
#         form = PasswordForm(request.user)
#     context = {
#         'form': form,
#     }
#     return request.dmp.render('password.html', context)
