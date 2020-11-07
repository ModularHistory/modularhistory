from crispy_forms.helper import FormHelper
from crispy_forms.layout import HTML, Field, Layout, Submit
from django import forms
from django.http import HttpRequest

# TODO: this causes memory issue?
ENABLE_AUTOCOMPLETE = False
if ENABLE_AUTOCOMPLETE:
    from modularhistory.constants.topics import TOPICS

    AUTOCOMPLETE_CHOICES = [(topic, topic) for topic in TOPICS]


class SearchForm(forms.Form):
    """Form for searching for searchable model instances."""

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
            help_text='',
            # widget=Select2Widget(choices=AUTOCOMPLETE_CHOICES),  # TODO
        )

        # https://django-crispy-forms.readthedocs.io/en/latest/form_helper.html
        self.helper = FormHelper()
        self.helper.form_id = 'search-form'
        self.helper.form_method = 'get'
        self.helper.form_action = 'search'
        self.helper.form_class = 'text-center'
        self.helper.form_show_labels = False
        self.helper.layout = Layout(
            HTML('<p>Search modules by topic, entity, or keywords.</p>'),
            Field(
                'query',
                css_class='form-control',
                style='width: 20rem; max-width: 100%;',
            ),
            Submit('submit', 'Search'),
        )
