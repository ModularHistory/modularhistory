import logging
from typing import Dict, Optional

from django.forms import ModelForm
from polymorphic.admin import PolymorphicChildModelAdmin, PolymorphicParentModelAdmin

from admin import TabularInline, admin_site
from apps.search.admin import SearchableModelAdmin
from apps.sources import models
from apps.sources.admin.filters import (
    AttributeeFilter,
    HasContainerFilter,
    HasFileFilter,
    HasFilePageOffsetFilter,
    ImpreciseDateFilter,
    TypeFilter,
)
from apps.sources.admin.source_inlines import (
    AttributeesInline,
    ContainedSourcesInline,
    ContainersInline,
    PolymorphicAttributeesInline,
    PolymorphicContainedSourcesInline,
    PolymorphicContainersInline,
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
            extra: Dict = (instance.extra or {}) if instance else {}
            initial_extra_fields = initial.get(self.model.FieldNames.extra, {})
            for key in schema:
                initial_value = extra.get(key, None) if instance else None
                initial_extra_fields[key] = initial_value
            initial[models.Source.FieldNames.extra] = initial_extra_fields
        kwargs[INITIAL] = initial
        super().__init__(*args, **kwargs)


class PolymorphicSourceAdmin(PolymorphicParentModelAdmin, SearchableModelAdmin):

    base_model = models.PolymorphicSource
    child_models = (
        models.PolymorphicAffidavit,
        models.PolymorphicArticle,
        models.PolymorphicBook,
        models.PolymorphicCorrespondence,
        models.PolymorphicDocument,
        models.PolymorphicFilm,
        models.PolymorphicInterview,
        models.PolymorphicJournalEntry,
        models.PolymorphicPiece,
        models.PolymorphicSection,
        models.PolymorphicSpeech,
        models.PolymorphicWebPage,
    )
    list_display = [
        'pk',
        'escaped_citation_html',
        'attributee_string',
        'date_string',
        'admin_source_link',
        'slug',
        'ctype',
    ]
    list_filter = [
        models.Source.FieldNames.verified,
        # HasContainerFilter,
        # HasFileFilter,
        # HasFilePageOffsetFilter,
        # ImpreciseDateFilter,
        # models.Source.FieldNames.hidden,
        # AttributeeFilter,
        # TypeFilter,
    ]
    ordering = ['date', 'citation_string']
    search_fields = base_model.searchable_fields


class ChildSourceAdmin(PolymorphicChildModelAdmin):
    """ Base admin class for all child models """

    base_model = models.PolymorphicSource

    # # By using these `base_...` attributes instead of the regular ModelAdmin `form` and `fieldsets`,
    # # the additional fields of the child models are automatically added to the admin form.
    # base_form = ...
    # base_fieldsets = ...

    exclude = [
        'citation_html',
        'citation_string',
    ]
    inlines = [
        PolymorphicAttributeesInline,
        PolymorphicContainersInline,
        PolymorphicContainedSourcesInline,
        RelatedInline,
    ]
    list_display = [
        item for item in PolymorphicSourceAdmin.list_display if item != 'ctype'
    ]
    readonly_fields = SearchableModelAdmin.readonly_fields + [
        'escaped_citation_html',
        'citation_string',
        'computations',
    ]
    search_fields = base_model.searchable_fields


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
        'slug',
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


admin_site.register(models.PolymorphicSource, PolymorphicSourceAdmin)

admin_site.register(models.PolymorphicAffidavit, ChildSourceAdmin)
admin_site.register(models.PolymorphicArticle, ChildSourceAdmin)
admin_site.register(models.PolymorphicBook, ChildSourceAdmin)
admin_site.register(models.PolymorphicCorrespondence, ChildSourceAdmin)
admin_site.register(models.PolymorphicDocument, ChildSourceAdmin)
admin_site.register(models.PolymorphicFilm, ChildSourceAdmin)
admin_site.register(models.PolymorphicInterview, ChildSourceAdmin)
admin_site.register(models.PolymorphicJournalEntry, ChildSourceAdmin)
admin_site.register(models.PolymorphicPiece, ChildSourceAdmin)
admin_site.register(models.PolymorphicSection, ChildSourceAdmin)
admin_site.register(models.PolymorphicSpeech, ChildSourceAdmin)
admin_site.register(models.PolymorphicWebPage, ChildSourceAdmin)

admin_site.register(models.Source, SourceAdmin)
admin_site.register(models.Documentary, SourceAdmin)
admin_site.register(models.Speech, SpeechAdmin)
admin_site.register(models.Interview, SpeechAdmin)
