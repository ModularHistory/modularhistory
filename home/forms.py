from crispy_forms.bootstrap import Accordion, AccordionGroup
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit, Layout, Field, HTML, Div
from django.forms import Form, ModelMultipleChoiceField, CheckboxSelectMultiple
from django_select2.forms import Select2MultipleWidget
from entities.models import Entity
from places.models import Place
from topics.models import Topic

Accordion.template = 'forms/_accordion.html'
AccordionGroup.template = 'forms/_accordion_group.html'


class SearchFilterForm(Form):
    entities = ModelMultipleChoiceField(
        queryset=Entity.objects.all(),
        # widget=Select2MultipleWidget,
        required=False
    )
    topics = ModelMultipleChoiceField(
        queryset=Topic.objects.all(),
        # widget=Select2MultipleWidget,
        required=False
    )
    places = ModelMultipleChoiceField(
        queryset=Place.objects.all(),
        # widget=Select2MultipleWidget,
        required=False
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # https://django-crispy-forms.readthedocs.io/en/latest/form_helper.html
        self.helper = FormHelper()
        self.helper.form_id = 'refineSearchForm'
        self.helper.form_class = 'form-inline'
        self.helper.form_method = 'get'
        self.helper.form_action = 'search'
        # self.helper.label_class = 'col-lg-2'
        # self.helper.field_class = 'col-lg-8'
        # self.helper.add_input(Submit('submit', 'Submit'))
        self.helper.layout = Layout(
            Field('entities', css_class=''),
            Field('topics', css_class=''),
            Field('places', css_class=''),
            Submit('submit', 'Refine results'),
            # StrictButton('Sign in', css_class='btn-default'),
        )
