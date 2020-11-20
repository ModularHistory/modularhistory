import logging
from typing import Dict, Optional

from django.forms import ModelForm

from admin import TabularInline, admin_site
from admin.searchable_model_admin import SearchableModelAdmin
from sources import models
from sources.admin.filters import (
    AttributeeFilter,
    HasContainerFilter,
    HasFileFilter,
    HasFilePageOffsetFilter,
    ImpreciseDateFilter,
    TypeFilter,
)
from sources.admin.source_inlines import (
    AttributeesInline,
    ContainedSourcesInline,
    ContainersInline,
    RelatedInline,
)


INITIAL = 'initial'


class SourceForm(ModelForm):
    """Form for adding/editing sources."""

    model = models.Source

    class Meta:
        model = models.Source
        exclude = model.inapplicable_fields

    def __init__(self, *args, **kwargs):
        """Construct the source form."""
        instance: Optional[models.Source] = kwargs.get('instance', None)
        schema: Dict = (
            instance.extra_field_schema if instance else self.model.extra_field_schema
        )
        initial = kwargs.pop(INITIAL, {})
        if instance is None:
            source_type = f'sources.{self.model.__name__.lower()}'
            logging.debug(f'Setting initial type to {source_type}')
            initial['type'] = source_type
        if schema:
            extra = (instance.extra or {}) if instance else {}
            initial_extra_fields = initial.get(self.model.FieldNames.extra, {})
            for key in schema:
                initial_value = extra.get(key, None) if instance else None
                initial_extra_fields[key] = initial_value
            initial[models.Source.FieldNames.extra] = initial_extra_fields
        kwargs[INITIAL] = initial
        super().__init__(*args, **kwargs)


class SourceAdmin(SearchableModelAdmin):
    """Admin for sources."""

    model = models.Source
    form = SourceForm
    list_display = [
        model.FieldNames.pk,
        'html',
        'date_string',
        model.FieldNames.location,
        'admin_source_link',
        'type',
    ]
    list_filter = [
        model.FieldNames.verified,
        HasContainerFilter,
        HasFileFilter,
        HasFilePageOffsetFilter,
        ImpreciseDateFilter,
        model.FieldNames.hidden,
        AttributeeFilter,
        TypeFilter,
    ]
    readonly_fields = SearchableModelAdmin.readonly_fields + [
        model.FieldNames.string,
        'computations',
    ]
    search_fields = models.Source.searchable_fields
    ordering = ['date', model.FieldNames.string]
    inlines = [
        AttributeesInline,
        ContainersInline,
        ContainedSourcesInline,
        RelatedInline,
    ]
    autocomplete_fields = [model.FieldNames.file, model.FieldNames.location]

    # https://docs.djangoproject.com/en/3.1/ref/contrib/admin/#django.contrib.admin.ModelAdmin.list_per_page
    list_per_page = 10

    # https://docs.djangoproject.com/en/3.1/ref/contrib/admin/#django.contrib.admin.ModelAdmin.save_as
    save_as = True

    # https://docs.djangoproject.com/en/3.1/ref/contrib/admin/#django.contrib.admin.ModelAdmin.save_as_continue
    save_as_continue = True

    def get_fields(self, request, model_instance: Optional[models.Source] = None):
        """Return reordered fields to be displayed in the admin."""
        fields = list(super().get_fields(request, model_instance))
        inapplicable_fields = getattr(model_instance, 'inapplicable_fields', [])
        for field in inapplicable_fields:
            try:
                fields.remove(field)
            except Exception as err:
                logging.error(f'{err}')
        fields_to_move = (models.Source.FieldNames.string,)
        for field in fields_to_move:
            if field in fields:
                fields.remove(field)
                fields.insert(0, field)
        return fields


class SpeechForm(SourceForm):
    """Form for adding/editing speeches."""

    model = models.Speech


class SpeechAdmin(SourceAdmin):
    """Admin for speeches."""

    model = models.Speech
    form = SpeechForm
    list_display = ['string', model.FieldNames.location, 'date_string']
    search_fields = [model.FieldNames.string, 'location__name']


class SourcesInline(TabularInline):
    """Inline admin for sources."""

    model = models.Source
    extra = 0
    fields = [
        'verified',
        'hidden',
        'date_is_circa',
        'creators',
        model.FieldNames.url,
        'date',
        'publication_date',
    ]


admin_site.register(models.Source, SourceAdmin)
admin_site.register(models.Documentary, SourceAdmin)
admin_site.register(models.Speech, SpeechAdmin)
admin_site.register(models.Interview, SpeechAdmin)
