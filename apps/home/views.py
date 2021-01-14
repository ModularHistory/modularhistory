from typing import Dict

from django.views.generic import TemplateView  # , RedirectView

from apps.home.forms import SearchForm


class HomePageView(TemplateView):
    """Renders the homepage."""

    template_name = 'home/index.html'

    def get_context_data(self, **kwargs) -> Dict:
        """Return the context dictionary used to render the view."""
        context = super().get_context_data(**kwargs)
        search_form = SearchForm(request=self.request)
        context['search_form'] = search_form
        return context
