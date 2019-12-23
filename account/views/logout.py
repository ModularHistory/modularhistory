from account.models import User
from django import forms
from django.conf import settings
from django.contrib.auth import logout
from django.http import HttpResponseRedirect
from django_mako_plus import view_function, jscontext

@view_function
def process_request(request):
    # log the user out
    logout(request)
    return HttpResponseRedirect('/')
