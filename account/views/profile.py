from account.forms import ChangeForm, PictureForm
from account.models import User
from django.conf import settings
from django.contrib.auth.decorators import permission_required, login_required
from django.forms.models import model_to_dict
from django.http import HttpResponse, HttpResponseRedirect, Http404
from django.shortcuts import get_object_or_404
from django.utils import timezone
from django_mako_plus import view_function, jscontext
from imagekit.models import ImageSpecField
from imagekit.processors import ResizeToFill
import datetime

from account.models import User

@view_function
@login_required(login_url='/account/login')
def process_request(request):
    """User Details"""
    user = request.user
    if user.avatar:
        profile_image_url = user.avatar.url
    elif user.gender == 'F':
        profile_image_url = '%saccount/media/nobody_f.jpg' % settings.STATIC_URL
    else:
        profile_image_url = '%saccount/media/nobody_m.jpg' % settings.STATIC_URL
    context = {
        'user': user,
        'name': user.get_full_name(),
        'email': user.email,
        'profile_image_url': profile_image_url,
    }
    return request.dmp.render('profile.html', context)


@view_function
@login_required(login_url='/account/login')
def edit(request):
    """Page for editing user profile"""
    # process the form
    form = ChangeForm(request, instance=request.user)
    if form.is_valid():
        u = request.user
        if 'picture' in request.FILES:
            u.avatar = form.cleaned_data.get('picture')
        u.username = form.cleaned_data.get('username')
        u.first_name = form.cleaned_data.get('first_name')
        u.last_name = form.cleaned_data.get('last_name')
        u.email = form.cleaned_data.get('email')
        u.date_of_birth = form.cleaned_data.get('date_of_birth')
        u.address = form.cleaned_data.get('address')
        u.address2 = form.cleaned_data.get('address2')
        u.city = form.cleaned_data.get('city')
        u.state = form.cleaned_data.get('state')
        u.zip_code= form.cleaned_data.get('zip')
        u.phone_number = form.cleaned_data.get('phone_number')
        weight = form.cleaned_data.get('weight')
        if weight:
            u.weight = form.cleaned_data.get('weight')
            u.update_registered_weight(weight)
        u.belt = form.cleaned_data.get('belt')
        u.stripes = form.cleaned_data.get('stripes')
        u.save()
        for ep in u.event_participations.filter(event__datetime__gte=datetime.datetime.today()):
            ep.belt = form.cleaned_data.get('belt')
            ep.stripes = form.cleaned_data.get('stripes')
            ep.save()
        return HttpResponseRedirect('/account/profile/')
    context = {
        'form': form,
    }
    return request.dmp.render('profile.edit.html', context)


@view_function
@login_required(login_url='/account/login')
def picture(request):
    form = PictureForm(request, initial={ 'picture': request.user.avatar, })
    if form.is_valid():
        u = request.user
        u.avatar = form.cleaned_data.get('picture')
        u.save()
        redirect_url = '/account/profile/'
        return HttpResponse("""
            <p class="text-center" style="display: none">
                Uploaded successfully.  Redirecting...
            </p>
            <script>
                window.location.href = '%s';
            </script>
        """ % redirect_url)
    context = {
        'form': form,
    }
    return request.dmp.render('/home/templates/form.html', context)
