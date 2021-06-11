import re
from typing import Mapping, Optional, Type, Union

from aenum import Constant
from django.conf import settings
from django.contrib.admin import ListFilter
from django.contrib.admin import ModelAdmin as BaseModelAdmin
from django.contrib.contenttypes.models import ContentType
from django.contrib.sites.models import Site
from django.db.models import Model
from django.db.models.fields import Field
from django.db.models.query import QuerySet
from django.forms import CharField, TextInput, Widget
from django.http import HttpRequest
from django_celery_beat.admin import PeriodicTaskAdmin
from django_celery_beat.models import (
    CrontabSchedule,
    IntervalSchedule,
    PeriodicTask,
    SolarSchedule,
)
from django_celery_results.admin import TaskResultAdmin
from django_celery_results.models import TaskResult
from polymorphic.admin import PolymorphicInlineSupportMixin
from sass_processor.processor import sass_processor

from apps.admin.admin_site import admin_site
from apps.admin.widgets.historic_date_widget import HistoricDateWidget
from apps.admin.widgets.json_editor_widget import JSONEditorWidget
from apps.dates.fields import HistoricDateTimeField
from core.constants.environments import Environments
from core.fields.html_field import HTMLField, TrumbowygWidget
from core.fields.json_field import JSONField
from core.models.manager import SearchableQuerySet

AdminListFilter = Union[str, Type[ListFilter]]

char_counter_code = (
    'if ($(this)).attr("maxLength")) {{ console.log("yes") }} else {{ console.log("no") }}'
)

FORM_FIELD_OVERRIDES: Mapping[Type[Field], Mapping[str, Type[Widget]]] = {
    CharField: {
        'widget': TextInput(attrs={'onClick': char_counter_code, 'style': 'width: 100%'})
    },
    HistoricDateTimeField: {'widget': HistoricDateWidget},
    HTMLField: {'widget': TrumbowygWidget},
    JSONField: {'widget': JSONEditorWidget},
}

if settings.ENVIRONMENT == Environments.DEV:
    BASE_CSS = sass_processor('styles/base.scss')
    MCE_CSS = sass_processor('styles/mce.scss')
    ADMIN_CSS = sass_processor('styles/admin.scss')
else:
    BASE_CSS = 'styles/base.css'
    MCE_CSS = 'styles/mce.css'
    ADMIN_CSS = 'styles/admin.css'


class ModelAdmin(PolymorphicInlineSupportMixin, BaseModelAdmin):
    """Base admin class for ModularHistory's models."""

    model: Type[Model]

    formfield_overrides = FORM_FIELD_OVERRIDES

    class Media:
        css = {
            'all': (
                'https://use.fontawesome.com/releases/v5.11.2/css/all.css',
                '//cdnjs.cloudflare.com/ajax/libs/Trumbowyg/2.24.0/ui/trumbowyg.min.css',
                '//cdnjs.cloudflare.com/ajax/libs/Trumbowyg/2.24.0/plugins/table/ui/trumbowyg.table.min.css',
                BASE_CSS,
                ADMIN_CSS,
            )
        }
        js = (
            '//ajax.googleapis.com/ajax/libs/jquery/3.5.1/jquery.min.js',
            '//cdnjs.cloudflare.com/ajax/libs/Trumbowyg/2.24.0/trumbowyg.min.js',
            '//cdnjs.cloudflare.com/ajax/libs/Trumbowyg/2.24.0/plugins/table/trumbowyg.table.min.js',
            'scripts/admin.js',
        )

    def get_readonly_fields(
        self, request: HttpRequest, model_instance: Optional['Model'] = None
    ) -> list[str]:
        """Add additional readonly fields."""
        default_readonly_fields = ('cache',)
        readonly_fields = list(super().get_readonly_fields(request, model_instance))
        if model_instance:
            for additional_readonly_field in default_readonly_fields:
                if hasattr(model_instance, additional_readonly_field):  # noqa: WPS421
                    readonly_fields.append(additional_readonly_field)
        return list(set(readonly_fields))

    def get_search_results(
        self,
        request: HttpRequest,
        queryset: Union[QuerySet, SearchableQuerySet],
        search_term: str = '',
    ) -> tuple[QuerySet, bool]:
        """Return model instances matching the supplied search term."""
        search_term = search_term.strip()
        searchable_fields = (
            getattr(self.model, 'searchable_fields', None) or self.search_fields
        )
        # If the request comes from the admin edit page for a model instance,
        # exclude the model instance from the search results. This prevents
        # inline admins from displaying an unwanted value in an autocomplete
        # field or, in the worst-case scenario, letting an admin errantly
        # create a relationship between a model instance and itself.
        referer = request.META.get('HTTP_REFERER') or ''
        match = re.match(r'.+/(\d+)/change', referer)
        if match:
            pk = int(match.group(1))
            queryset = queryset.exclude(pk=pk)
        if isinstance(queryset, SearchableQuerySet):
            queryset, use_distinct = (
                queryset.search(search_term, elastic=False, fields=searchable_fields),
                False,
            )
        else:
            queryset, use_distinct = super().get_search_results(
                request, queryset, search_term
            )
        return queryset, use_distinct


class ContentTypeFields(Constant):
    """Field names of the ContentType model."""

    pk = 'pk'
    app_label = 'app_label'
    model = 'model'


class ContentTypeAdmin(ModelAdmin):
    """Admin for content types."""

    model = ContentType
    list_display = [
        ContentTypeFields.app_label,
        ContentTypeFields.model,
        ContentTypeFields.pk,
    ]
    list_filter = [ContentTypeFields.app_label]
    readonly_fields = [
        ContentTypeFields.app_label,
        ContentTypeFields.model,
        ContentTypeFields.pk,
    ]
    ordering = [ContentTypeFields.app_label]


admin_site.register(ContentType, ContentTypeAdmin)


class SiteAdmin(ModelAdmin):
    """
    Admin for sites.

    Ref: https://docs.djangoproject.com/en/dev/ref/contrib/sites/
    """

    model = Site
    list_display = ['pk', 'name', 'domain']


admin_site.register(Site, SiteAdmin)

admin_site.register(IntervalSchedule)
admin_site.register(CrontabSchedule)
admin_site.register(SolarSchedule)
admin_site.register(PeriodicTask, PeriodicTaskAdmin)
admin_site.register(TaskResult, TaskResultAdmin)
