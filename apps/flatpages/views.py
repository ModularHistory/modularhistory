from django.conf import settings
from django.contrib.sites.models import Site
from django.contrib.sites.shortcuts import get_current_site
from django.http import Http404, HttpResponse, HttpResponsePermanentRedirect
from django.shortcuts import get_object_or_404
from django.template import loader
from django.utils.html import format_html
from django.views.decorators.csrf import csrf_protect

from apps.flatpages.models import FlatPage
from core.constants.strings import SLASH

DEFAULT_TEMPLATE = 'flatpages/default.html'

# This view is called from FlatPageFallbackMiddleware.process_response
# when a 404 is raised, which often means CsrfViewMiddleware.process_view
# has not been called even if CsrfViewMiddleware is installed. So we need
# to use @csrf_protect, in case the template needs {% csrf_token %}.
# However, we can't just wrap this view; if no matching static page exists,
# or a redirect is required for authentication, the 404 needs to be returned
# without any CSRF checks. Therefore, we only
# CSRF protect the internal implementation.


def flatpage(request, path):
    """
    Public interface to the flatpage view.

    Templates:
        Uses the template defined by the ``template_name`` field,
        or :template:`flatpages/default.html` if template_name is not defined.
    Context:
        flatpage
            `flatpages.flatpages` obj
    """
    if not path.startswith(SLASH):
        path = f'/{path}'
    site = get_current_site(request)
    site_id = site.id if isinstance(site, Site) else 1
    try:
        flatpage = get_object_or_404(FlatPage, path=path, sites=site_id)
    except Http404:
        if not path.endswith(SLASH) and settings.APPEND_SLASH:
            path = f'{path}/'
            flatpage = get_object_or_404(FlatPage, path=path, sites=site_id)
            return HttpResponsePermanentRedirect(f'{request.path}/')
        raise
    return render_flatpage(request, flatpage)


@csrf_protect
def render_flatpage(request, static_page: FlatPage):
    """Render the flatpage view."""
    # If registration is required for accessing this page, and the user isn't
    # logged in, redirect to the login page.
    if static_page.registration_required and not request.user.is_authenticated:
        from django.contrib.auth.views import redirect_to_login

        return redirect_to_login(request.path)
    if static_page.template_name:
        template = loader.select_template([static_page.template_name, DEFAULT_TEMPLATE])
    else:
        template = loader.get_template(DEFAULT_TEMPLATE)

    # To avoid having to always use the "|safe" filter in static page templates,
    # mark the title and content as already safe (since they are raw HTML
    # content in the first place).
    static_page.title = format_html(static_page.title)
    static_page.content = format_html(static_page.content)  # noqa: WPS110

    return HttpResponse(template.render({'page': static_page}, request))
