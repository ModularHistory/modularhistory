from django.contrib.auth import authenticate, login
from django.contrib.auth import views as auth_views
from django.http import HttpRequest, HttpResponse
from django.shortcuts import render, redirect
from django.views.generic import View

from account.forms import LoginForm, RegistrationForm
from account.models import User


class LoginView(auth_views.LoginView):
    """Login view."""

    form_class = LoginForm
    template_name = 'account/login.html'


LogoutView = auth_views.LogoutView


class RegisterView(View):
    """Account registration view."""

    def get(self, request: HttpRequest) -> HttpResponse:
        """Renders the registration view when the page is requested."""
        form: RegistrationForm = RegistrationForm()
        context = {'form': form}
        return render(request, 'account/register.html', context)

    def post(self, request: HttpRequest) -> HttpResponse:
        """Responds to registration form submission."""
        form: RegistrationForm = RegistrationForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get('username')
            raw_password = form.cleaned_data.get('password1')
            user = authenticate(username=username, password=raw_password)
            if isinstance(user, User):
                login(request, user)
                return redirect('/')
            else:
                print(f'Unexpected authentication result: {type(user)}: {user}')
        return render(request, 'account/register.html', {'form': form})


# from account.forms import ChangeForm, PictureForm

# @view_function
# @login_required(login_url='/account/login')
# def process_request(request):
#     """User Details."""
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
#     """Page for editing user profile."""
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
