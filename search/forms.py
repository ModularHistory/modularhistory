from typing import List, Optional, Tuple

from crispy_forms.bootstrap import Accordion, AccordionGroup
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit, Layout, Field
from django.db.models import QuerySet
from django.forms import (
    Form,
    CharField,
    ChoiceField,
    ModelMultipleChoiceField,
    CheckboxSelectMultiple,
    MultipleChoiceField,
    RadioSelect
)

from entities.models import Entity
from django_select2.forms import Select2MultipleWidget
from history.forms import HistoricDateFormField
from history.widgets.historic_date_widget import YearInput
# from places.models import Place
from topics.models import Topic

Accordion.template = 'forms/_accordion.html'
AccordionGroup.template = 'forms/_accordion_group.html'


ordering_choices = (
    ('date', 'Date'),
    ('relevance', 'Relevance')
)


class SearchFilterForm(Form):
    SUBMIT_BUTTON_TEXT = 'Refine results'

    def __init__(
            self,
            query: Optional[str] = None,
            order_by_relevance: bool = False,
            content_types: List[Tuple[int, str]] = None,
            entities: Optional[QuerySet] = None,
            topics: Optional[QuerySet] = None,
            # places: Optional[QuerySet] = None,
            *args,
            **kwargs
    ):
        super().__init__(*args, **kwargs)

        self.fields['query'] = CharField(required=False, initial=query)

        ordering = 'relevance' if order_by_relevance else 'date'
        self.fields['ordering'] = ChoiceField(
            choices=ordering_choices,
            widget=RadioSelect,
            initial=ordering,
            required=False
        )
        if not query:
            self.fields['ordering'].widget.attrs['disabled'] = True

        self.fields['content_types'] = MultipleChoiceField(
            choices=content_types,
            widget=CheckboxSelectMultiple,
            required=False
        )

        self.fields['start_year'] = HistoricDateFormField(required=False, widget=YearInput)
        self.fields['end_year'] = HistoricDateFormField(required=False, widget=YearInput)

        self.fields['entities'] = ModelMultipleChoiceField(
            queryset=(entities or Entity.objects.all()),
            widget=Select2MultipleWidget,
            required=False
        )
        self.fields['topics'] = ModelMultipleChoiceField(
            queryset=(topics or Topic.objects.all()),
            widget=Select2MultipleWidget,
            required=False
        )
        # self.fields['places'] = ModelMultipleChoiceField(
        #     queryset=(places or Place.objects.all()),
        #     # widget=Select2MultipleWidget,
        #     required=False
        # )

        # https://django-crispy-forms.readthedocs.io/en/latest/form_helper.html
        self.helper = FormHelper()
        self.helper.form_id = 'refineSearchForm'
        # self.helper.form_class = 'd-none'
        self.helper.form_method = 'get'
        self.helper.form_action = 'search'
        # self.helper.label_class = 'col-lg-2'
        # self.helper.field_class = 'col-lg-8'
        # self.helper.add_input(Submit('submit', 'Submit'))
        self.helper.layout = Layout(
            Field('query', css_class='form-control'),
            Field('ordering', css_class=''),
            Field('start_year'),
            Field('end_year'),
            Field('entities', css_class=''),
            Field('topics', css_class=''),
            # Field('places', css_class=''),
            Field('content_types', css_class=''),
            Submit('submit', self.SUBMIT_BUTTON_TEXT),
        )
