from account.forms import LoginForm, RegisterForm
from account.models import User
from django import forms
from django.conf import settings
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm
from django.http import HttpResponse, HttpResponseRedirect
from django_mako_plus import view_function, jscontext

@view_function
def process_request(request):
    """Log in"""
    # process the form
    print(">>> Entering login.py process_request with URL %s" % request.build_absolute_uri())
    template = 'login_ajax.html' if 'ajax' in request.GET else 'login.html'
    print(">>> Next URL is %s..." % (request.GET.get('next') if 'next' in request.GET else '[none]'))
    loginform = LoginForm(initial={ 'next': request.GET.get('next') }) if 'next' in request.GET else LoginForm()
    registerform = RegisterForm(request, initial={ 'next': request.GET.get('next') }) if 'next' in request.GET else RegisterForm(request)
    if request.method == 'POST':
        loginform = LoginForm(request.POST)
        if loginform.is_valid():
            # log the user in
            login(request, loginform.user)
            if not request.user.force_password_change:
                redirect_url = '/home/' if not loginform.cleaned_data.get('next') else loginform.cleaned_data.get('next')
                return HttpResponse("""
                    <p class="text-center">
                        Authenticated successfully.  Redirecting...
                    </p>
                    <script>
                        window.location.href = '%s';
                    </script>
                """ % redirect_url)
            else:
                return HttpResponse("""
                    <script>
                        $('.modal-title').text('Change your password');
                        $('#jquery-loadmodal-js-body').load('/account/settings.password/');
                    </script>
                """)
    # print(">>> Next URL is %s..." % (form.data.get('next') if form.data.get('next') else '[none]'))
    context = {
        'loginform': loginform,
        'registerform': registerform,
    }
    print(">>> Returning %s..." % template)
    return request.dmp.render(template, context)
