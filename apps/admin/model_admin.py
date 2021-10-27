import re
from typing import Mapping, Optional, Union

from aenum import Constant
from django.conf import settings
from django.contrib.admin import ListFilter
from django.contrib.admin import ModelAdmin as BaseModelAdmin
from django.contrib.contenttypes.models import ContentType
from django.contrib.sites.models import Site
from django.db.models import Model
from django.db.models.fields import Field
from django.db.models.query import QuerySet
from django.forms import Widget
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

AdminListFilter = Union[str, type[ListFilter]]

FORM_FIELD_OVERRIDES: Mapping[type[Field], Mapping[str, type[Widget]]] = {
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

CSS = {
    'all': (
        'https://use.fontawesome.com/releases/v5.11.2/css/all.css',
        BASE_CSS,
        ADMIN_CSS,
    )
}
JS = ('scripts/admin.js',)


class ExtendedModelAdmin(PolymorphicInlineSupportMixin, BaseModelAdmin):
    """Base admin class for ModularHistory's models."""

    model: type[Model]

    formfield_overrides = FORM_FIELD_OVERRIDES

    class Media:
        css = {
            'all': (
                'https://use.fontawesome.com/releases/v5.11.2/css/all.css',
                BASE_CSS,
                ADMIN_CSS,
            )
        }
        js = (
            '//ajax.googleapis.com/ajax/libs/jquery/3.5.1/jquery.min.js',
            'scripts/admin.js',
        )

    def get_exclude(self, request: HttpRequest, obj: Optional['Model'] = None) -> list[str]:
        """Return the fields to exclude from admin forms."""
        always_excluded_fields = ('cache',)
        excluded_fields = list(super().get_exclude(request, obj=obj) or [])
        if obj:
            for excluded_field in always_excluded_fields:
                if hasattr(obj, excluded_field):  # noqa: WPS421
                    excluded_fields.append(excluded_field)
        return list(set(excluded_fields))

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


class ContentTypeAdmin(ExtendedModelAdmin):
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


class SiteAdmin(ExtendedModelAdmin):
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
