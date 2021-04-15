from typing import List, Optional, Type, Union

from aenum import Constant
from django.conf import settings
from django.contrib.admin import ListFilter
from django.contrib.contenttypes.models import ContentType
from django.contrib.sites.models import Site
from django.http import HttpRequest
from django_celery_beat.admin import PeriodicTaskAdmin
from django_celery_beat.models import (
    CrontabSchedule,
    IntervalSchedule,
    PeriodicTask,
    SolarSchedule,
)
from django_celery_results.admin import TaskResult, TaskResultAdmin
from nested_admin.nested import NestedModelAdmin
from sass_processor.processor import sass_processor

from admin.admin_site import admin_site
from core.constants.environments import Environments
from core.fields import HistoricDateTimeField, JSONField
from core.forms import HistoricDateWidget
from core.models import Model
from core.widgets.json_editor_widget import JSONEditorWidget

AdminListFilter = Union[str, Type[ListFilter]]


FORM_FIELD_OVERRIDES = {
    HistoricDateTimeField: {'widget': HistoricDateWidget},
    JSONField: {'widget': JSONEditorWidget()},
}

if settings.ENVIRONMENT == Environments.DEV:
    BASE_CSS = sass_processor('styles/base.scss')
    MCE_CSS = sass_processor('styles/mce.scss')
    ADMIN_CSS = sass_processor('styles/admin.scss')
else:
    BASE_CSS = 'styles/base.css'
    MCE_CSS = 'styles/mce.css'
    ADMIN_CSS = 'styles/admin.css'


class ModelAdmin(NestedModelAdmin):
    """Base admin class for ModularHistory's models."""

    formfield_overrides = FORM_FIELD_OVERRIDES

    list_display: List[str]
    list_filter: List[AdminListFilter]
    ordering: List[str]
    readonly_fields: List[str]
    search_fields: List[str]
    autocomplete_fields: List[str]

    class Media:
        css = {
            'all': (
                'https://use.fontawesome.com/releases/v5.11.2/css/all.css',
                # 'https://maxcdn.bootstrapcdn.com/bootstrap/4.4.1/css/bootstrap.min.css',  # TODO
                BASE_CSS,
                MCE_CSS,
                ADMIN_CSS,
            )
        }
        js = (
            '//ajax.googleapis.com/ajax/libs/jquery/3.4.1/jquery.min.js',  # jQuery
            '//maxcdn.bootstrapcdn.com/bootstrap/4.4.1/js/bootstrap.min.js',  # Bootstrap
            '//cdn.jsdelivr.net/npm/epubjs/dist/epub.min.js',  # EPub.JS
            'scripts/base.js',
        )

    def get_readonly_fields(
        self, request: HttpRequest, model_instance: Optional['Model'] = None
    ) -> List[str]:
        """Add additional readonly fields."""
        default_readonly_fields = ('computations',)
        readonly_fields = list(super().get_readonly_fields(request, model_instance))
        if model_instance:
            for additional_readonly_field in default_readonly_fields:
                if hasattr(model_instance, additional_readonly_field):  # noqa: WPS421
                    readonly_fields.append(additional_readonly_field)
        return list(set(readonly_fields))


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

    Ref: https://docs.djangoproject.com/en/3.1/ref/contrib/sites/
    """

    model = Site
    list_display = ['pk', 'name', 'domain']


admin_site.register(Site, SiteAdmin)

admin_site.register(IntervalSchedule)
admin_site.register(CrontabSchedule)
admin_site.register(SolarSchedule)
admin_site.register(PeriodicTask, PeriodicTaskAdmin)
admin_site.register(TaskResult, TaskResultAdmin)
