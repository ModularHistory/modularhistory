from typing import List, TYPE_CHECKING, Tuple, Type, Union

from django.contrib.admin import ListFilter
from django.contrib.contenttypes.models import ContentType
from django.contrib.sites.models import Site
from django.db.models import JSONField
from django.db.models.query import QuerySet
from django.http.request import HttpRequest
from django_celery_beat.admin import (
    CrontabSchedule,
    IntervalSchedule,
    PeriodicTask,
    PeriodicTaskAdmin,
    SolarSchedule
)
from django_celery_results.admin import TaskResult, TaskResultAdmin
from django_json_widget.widgets import JSONEditorWidget
from nested_admin.nested import NestedModelAdmin
from sass_processor.processor import sass_processor
from social_django.admin import AssociationOption, NonceOption, UserSocialAuthOption
from social_django.models import Association, Nonce, UserSocialAuth

from admin.admin_site import admin_site
from modularhistory import environments, settings
from modularhistory.fields import HistoricDateTimeField, SourceFileField
from modularhistory.forms import HistoricDateWidget, SourceFileInput

if TYPE_CHECKING:
    from modularhistory.models import SearchableModel

FORM_FIELD_OVERRIDES = {
    HistoricDateTimeField: {'widget': HistoricDateWidget},
    SourceFileField: {'widget': SourceFileInput},
    JSONField: {'widget': JSONEditorWidget}
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
    list_filter: List[Union[str, Type[ListFilter]]]
    ordering: List[str]
    readonly_fields: List[str]
    search_fields: List[str]
    autocomplete_fields: List[str]

    class Media:
        css = {
            'all': (
                'https://use.fontawesome.com/releases/v5.11.2/css/all.css',
                BASE_CSS, MCE_CSS, ADMIN_CSS,
            )
        }
        js = (
            '//ajax.googleapis.com/ajax/libs/jquery/3.4.1/jquery.min.js',  # jQuery
            '//maxcdn.bootstrapcdn.com/bootstrap/4.4.1/js/bootstrap.min.js',  # Bootstrap
            '//cdn.jsdelivr.net/npm/epubjs/dist/epub.min.js',  # EPub.JS
            'scripts/mce.js',
            'scripts/base.js'
        )


class SearchableModelAdmin(ModelAdmin):
    """Model admin for searchable models."""

    model: Type['SearchableModel']

    def get_search_results(
        self, request: HttpRequest, queryset: QuerySet, search_term: str
    ) -> Tuple[QuerySet, bool]:
        """Custom implementation for searching sources in the admin."""
        queryset, use_distinct = super().get_search_results(request, queryset, search_term)
        if search_term:
            print(f'Django admin search function returned queryset: {queryset}')
            print(f'Falling back on sources.manager.search with query={search_term}...')
            queryset = self.model.objects.search(search_term, suppress_unverified=False)
        return queryset, use_distinct


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
#     'https://maps.googleapis.com/maps/api/geocode/json?address={0}&key={1}'.format(address, api_key)
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


class ContentTypeAdmin(ModelAdmin):
    """Admin for content types."""

    model = ContentType
    list_display = ['app_label', 'model', 'pk']
    list_filter = ['app_label']
    readonly_fields = ['pk', 'app_label', 'model']
    ordering = ['app_label']


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

admin_site.register(UserSocialAuth, UserSocialAuthOption)
admin_site.register(Nonce, NonceOption)
admin_site.register(Association, AssociationOption)

# admin_site.register(PeriodicTask, CustomPeriodicTaskAdmin)
# admin_site.register(IntervalSchedule)
# admin_site.register(CrontabSchedule)
# admin_site.register(TaskResult, TaskResultAdmin)
