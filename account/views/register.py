from account.forms import RegisterForm, LoginForm
from account.models import User
from django import forms
from django.conf import settings
from django.contrib.auth import authenticate, login
from django.http import HttpResponse, HttpResponseRedirect
from django.utils import timezone
from django_mako_plus import view_function, jscontext

import datetime


@view_function
def process_request(request):
    """Sign up"""
    # process the form
    print(">>> Entering account / register / process_request...")
    registerform = RegisterForm(request, initial={ 'next': request.GET.get('next') }) if 'next' in request.GET else RegisterForm(request)
    if registerform.is_valid(): # If the form has been submitted and is valid
        print(">>> The form was posted and is valid...")
        u = User()
        u.email = registerform.cleaned_data.get('username')
        u.username = u.email
        u.first_name = registerform.cleaned_data.get('first_name')
        u.last_name = registerform.cleaned_data.get('last_name')
        # u.address = registerform.cleaned_data.get('address')
        # u.address2 = registerform.cleaned_data.get('address2')
        # u.city = registerform.cleaned_data.get('city')
        # u.state = registerform.cleaned_data.get('state')
        # u.zip_code = registerform.cleaned_data.get('zip_code')
        # u.date_of_birth = registerform.cleaned_data.get('date_of_birth')
        # u.phone_number = registerform.cleaned_data.get('phone_number')
        u.set_password(registerform.cleaned_data.get('password'))
        u.save()
        # Log the user in
        user = authenticate(username=registerform.cleaned_data.get('username'), password=registerform.cleaned_data.get('password'))
        if user is not None:
            login(request, user)    # Log in with the user retrieved from the authenticate method
            redirect_url = registerform.cleaned_data.get('next') if registerform.cleaned_data.get('next') else '/home/'
            print(">>> Redirecting to %s..." % redirect_url)
            return HttpResponseRedirect(redirect_url)
            # return HttpResponse("""
            #     <p>You have registered successfully.  Redirecting...</p>
            #     <script>
            #         window.location.href = '%s';
            #     </script>
            # """ % redirect_url)
    print(">>> The form has not yet been posted or was posted in an invalid state.")
    context = {
        'registerform': registerform,
    }
    return request.dmp.render('register.html', context)
