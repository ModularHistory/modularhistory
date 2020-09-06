from django.conf import settings
from .models import StaticPage
from django.contrib.sites.shortcuts import get_current_site
from django.http import Http404, HttpResponse, HttpResponsePermanentRedirect
from django.shortcuts import get_object_or_404
from django.template import loader
from django.utils.safestring import mark_safe
from django.views.decorators.csrf import csrf_protect

DEFAULT_TEMPLATE = 'staticpages/default.html'

# This view is called from StaticPageFallbackMiddleware.process_response
# when a 404 is raised, which often means CsrfViewMiddleware.process_view
# has not been called even if CsrfViewMiddleware is installed. So we need
# to use @csrf_protect, in case the template needs {% csrf_token %}.
# However, we can't just wrap this view; if no matching staticpage exists,
# or a redirect is required for authentication, the 404 needs to be returned
# without any CSRF checks. Therefore, we only
# CSRF protect the internal implementation.


def staticpage(request, url):
    """
    Public interface to the staticpage view.

    Models: `staticpages.staticpages`
    Templates: Uses the template defined by the ``template_name`` field,
        or :template:`staticpages/default.html` if template_name is not defined.
    Context:
        staticpage
            `staticpages.staticpages` object
    """
    if not url.startswith('/'):
        url = f'/{url}'
    site_id = get_current_site(request).id
    try:
        f = get_object_or_404(StaticPage, url=url, sites=site_id)
    except Http404:
        if not url.endswith('/') and settings.APPEND_SLASH:
            url += '/'
            f = get_object_or_404(StaticPage, url=url, sites=site_id)
            return HttpResponsePermanentRedirect(f'{request.path}/')
        else:
            raise
    return render_staticpage(request, f)


@csrf_protect
def render_staticpage(request, f):
    """
    Internal interface to the flat page view.
    """
    # If registration is required for accessing this page, and the user isn't
    # logged in, redirect to the login page.
    if f.registration_required and not request.user.is_authenticated:
        from django.contrib.auth.views import redirect_to_login
        return redirect_to_login(request.path)
    if f.template_name:
        template = loader.select_template([f.template_name, DEFAULT_TEMPLATE])
    else:
        template = loader.get_template(DEFAULT_TEMPLATE)

    # To avoid having to always use the "|safe" filter in staticpage templates,
    # mark the title and content as already safe (since they are raw HTML
    # content in the first place).
    f.title = mark_safe(f.title)
    f.content = mark_safe(f.content)

    return HttpResponse(template.render({'page': f}, request))
