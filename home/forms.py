from crispy_forms.helper import FormHelper
from crispy_forms.layout import Field, Layout, Submit
from django import forms
from django.http import HttpRequest
from django_select2.forms import Select2Widget

from modularhistory.constants.topics import TOPICS

AUTOCOMPLETE_CHOICES = [(topic, topic) for topic in TOPICS]


class SearchForm(forms.Form):
    """Form for searching for searchable model instances."""

    submit_button_text = 'Search'

    def __init__(
        self,
        request: HttpRequest,
        *args,
        **kwargs,
    ):
        """Construct the search form."""
        super().__init__(*args, **kwargs)
        self.request = request
        self.fields['query'] = forms.CharField(
            required=False,
            # widget=Select2Widget(choices=AUTOCOMPLETE_CHOICES),  # TODO
        )

        # https://django-crispy-forms.readthedocs.io/en/latest/form_helper.html
        self.helper = FormHelper()
        self.helper.form_id = 'search-form'
        self.helper.form_method = 'get'
        self.helper.form_action = 'search'
        self.helper.form_class = 'text-center'
        self.helper.form_show_labels = False
        layout = [
            Field('query', css_class='form-control', style='width: 20rem; max-width: 100%;'),
            Submit('submit', self.submit_button_text),
        ]
        self.helper.layout = Layout(*layout)
