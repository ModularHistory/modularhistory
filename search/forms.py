from typing import List, Optional, Tuple

from crispy_forms.bootstrap import Accordion, AccordionGroup
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit, Layout, Field, Div, HTML
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
from django.http import HttpRequest
from django_select2.forms import Select2MultipleWidget

from entities.models import Entity
from history.forms import HistoricDateFormField
from history.widgets.historic_date_widget import YearInput
# from django.core.paginator import Paginator
from topics.models import Topic
from .models import Search

Accordion.template = 'forms/_accordion.html'
AccordionGroup.template = 'forms/_accordion_group.html'


class SearchForm(Form):
    SUBMIT_BUTTON_TEXT = 'Search'

    def __init__(
            self,
            request: HttpRequest,
            query: Optional[str] = None,
            suppress_unverified: bool = True,
            order_by_relevance: bool = False,
            excluded_content_types: List[int] = None,
            entities: Optional[QuerySet] = None,
            topics: Optional[QuerySet] = None,
            # places: Optional[QuerySet] = None,
            db: str = 'default',
            collapse_refinements: bool = False,
            *args,
            **kwargs
    ):
        super().__init__(*args, **kwargs)
        excluded_content_types = excluded_content_types or []
        self.request = request
        self.fields['query'] = CharField(required=False, initial=query)
        ordering = 'relevance' if order_by_relevance else 'date'
        self.fields['ordering'] = ChoiceField(
            choices=Search.ORDERING_OPTIONS,
            widget=RadioSelect,
            initial=ordering,
            required=False
        )

        # Disable sorting by relevance if there are no criteria
        if not any([query, entities, topics]):
            self.fields['ordering'].widget.attrs['disabled'] = True

        # Filter unverified items
        quality = 'verified' if suppress_unverified else 'unverified'
        self.fields['quality'] = ChoiceField(
            choices=(('verified', 'Verified'), ('unverified', 'Unverified')),
            widget=RadioSelect,
            initial=quality,
            required=False
        )
        if not self.request.user.is_superuser:
            self.fields['quality'].widget.attrs['disabled'] = True

        # TODO: optimize
        content_type_options = Search.get_content_type_options()
        initial_content_types = [pk for pk, name in content_type_options if pk not in excluded_content_types]
        self.fields['content_types'] = MultipleChoiceField(
            choices=content_type_options,
            widget=CheckboxSelectMultiple,
            initial=initial_content_types,
            required=False
        )

        self.fields['start_year'] = HistoricDateFormField(required=False, widget=YearInput)
        self.fields['end_year'] = HistoricDateFormField(required=False, widget=YearInput)

        self.fields['entities'] = ModelMultipleChoiceField(
            queryset=(entities or Entity.objects.using(db).all()),
            widget=Select2MultipleWidget,
            required=False
        )
        self.fields['topics'] = ModelMultipleChoiceField(
            queryset=(topics or Topic.objects.using(db).all()),
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

        layout = [
            HTML('<div class="flexbox-holy-albatross">'),
            Field('query', css_class='form-control'),
            Field('ordering', css_class=''),
            HTML('</div>'),

            HTML('''
                <div class="card card-default">
                    <div class="card-header">
                        <h4 class="card-title">
                            <a class="collapsed" data-toggle="collapse" href="#searchRefinements">
                                Refinements 
                                <i class="fa fa-chevron-circle-up"></i>
                                <i class="fa fa-chevron-circle-down"></i>
                            </a>
                        </h4>
                    </div>
                    <div id="searchRefinements" class="card-collapse collapse">
                        <div class="card-body flexbox-holy-albatross">
            ''') if collapse_refinements else HTML('<div class="flexbox-holy-albatross">'),
            # date range
            Div('start_year', css_class=''),
            Div('end_year', css_class=''),
            Field('entities', css_class=''),
            Field('topics', css_class=''),
            Div('quality', css_class=''),
            Div('content_types', css_class=''),
            HTML('</div></div></div>') if collapse_refinements else HTML('</div>'),

            Submit('submit', self.SUBMIT_BUTTON_TEXT),
        ]
        self.helper.layout = Layout(*layout)
