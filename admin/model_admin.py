from typing import List, Optional, Tuple, Type, Union

from aenum import Constant
from django.contrib.admin import ListFilter
from django.contrib.contenttypes.models import ContentType
from django.contrib.sites.models import Site
from django.db.models import JSONField
from django.http import HttpRequest
from django_celery_beat.admin import (
    CrontabSchedule,
    IntervalSchedule,
    PeriodicTask,
    PeriodicTaskAdmin,
    SolarSchedule,
)
from django_celery_results.admin import TaskResult, TaskResultAdmin
from django_json_widget.widgets import JSONEditorWidget
from nested_admin.nested import NestedModelAdmin
from sass_processor.processor import sass_processor

from admin.admin_site import admin_site
from modularhistory import environments, settings
from modularhistory.fields import HistoricDateTimeField, SourceFileField
from modularhistory.forms import HistoricDateWidget, SourceFileInput
from modularhistory.models import Model

AdminListFilter = Union[str, Type[ListFilter]]

FORM_FIELD_OVERRIDES = {
    HistoricDateTimeField: {'widget': HistoricDateWidget},
    SourceFileField: {'widget': SourceFileInput},
    JSONField: {'widget': JSONEditorWidget},
}

if settings.ENVIRONMENT == environments.DEV:
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
                BASE_CSS,
                MCE_CSS,
                ADMIN_CSS,
            )
        }
        js = (
            '//ajax.googleapis.com/ajax/libs/jquery/3.4.1/jquery.min.js',  # jQuery
            '//maxcdn.bootstrapcdn.com/bootstrap/4.4.1/js/bootstrap.min.js',  # Bootstrap
            '//cdn.jsdelivr.net/npm/epubjs/dist/epub.min.js',  # EPub.JS
            'scripts/mce.js',
            'scripts/base.js',
        )

    def get_readonly_fields(
        self, request: HttpRequest, model_instance: Optional[Model] = None
    ) -> Union[List[str], Tuple]:
        """Add additional readonly fields."""
        default_readonly_fields = ('computations',)
        readonly_fields = super().get_readonly_fields(request, model_instance)
        if model_instance:
            for additional_readonly_field in default_readonly_fields:
                if hasattr(model_instance, additional_readonly_field):
                    readonly_fields.append(additional_readonly_field)
        return list(set(readonly_fields))


# IntervalSchedule.objects.get_or_create(
#     every=1,
#     period=IntervalSchedule.DAYS
# )
# CrontabSchedule.objects.get_or_create(
#     # minute='*',
#     hour='1',
#     day_of_week='1',
#     day_of_month='*',
#     month_of_year='*',
# )
# latitude = '40.23380'
# longitude = '-111.65850'
# # address = settings.SERVER_LOCATION
# # api_key = settings.GOOGLE_MAPS_API_KEY
# response = requests.get(
#     f'https://maps.googleapis.com/maps/api/geocode/json?address={address}&key={api_key}'
# ).json()
# # if response['status'] == 'OK':
# #     latitude = response['results'][0]['geometry']['location']['lat']
# #     longitude = response['results'][0]['geometry']['location']['lng']
# SolarSchedule.objects.get_or_create(
#     event='sunset',
#     latitude=latitude,
#     longitude=longitude,
# )
#
# class CustomPeriodicTaskForm(PeriodicTaskForm):
#     pass
#
# class CustomPeriodicTaskAdmin(PeriodicTaskAdmin):
#     fieldsets = (
#         (None, {
#             u'fields': (u'name', u'regtask', u'task', u'enabled', u'description'),
#             u'classes': (u'extrapretty', u'wide')
#         }),
#         (u'Schedule', {
#             u'fields': (u'interval', u'crontab', u'solar'),
#             u'classes': (u'extrapretty', u'wide')
#         }),
#         (u'Arguments', {
#             u'fields': (u'args', u'kwargs'),
#             u'classes': (u'extrapretty', u'wide', u'collapse', u'in')
#         }),
#         (u'Execution Options', {
#             u'fields': (u'expires', u'queue', u'exchange', u'routing_key'),
#             u'classes': (u'extrapretty', u'wide', u'collapse', u'in')
#         })
#     )
#     form = CustomPeriodicTaskForm


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

admin_site.register(PeriodicTask, PeriodicTaskAdmin)
admin_site.register(SolarSchedule)
admin_site.register(IntervalSchedule)
admin_site.register(CrontabSchedule)

admin_site.register(TaskResult, TaskResultAdmin)

# admin_site.register(PeriodicTask, CustomPeriodicTaskAdmin)
# admin_site.register(IntervalSchedule)
# admin_site.register(CrontabSchedule)
# admin_site.register(TaskResult, TaskResultAdmin)
