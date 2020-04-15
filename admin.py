from django.contrib.admin import AdminSite as BaseAdminSite
from django.contrib.contenttypes.models import ContentType
# from django.utils.translation import gettext_lazy as _
# from django_celery_beat.models import (
#     PeriodicTask, PeriodicTasks, CrontabSchedule, IntervalSchedule, SolarSchedule
# )
# from django_celery_beat.admin import PeriodicTaskAdmin, PeriodicTaskForm
# from django_celery_results.models import TaskResult
# from django_celery_results.admin import TaskResultAdmin
from django.contrib.flatpages.admin import FlatPageAdmin
from django.contrib.flatpages.models import FlatPage
from django.contrib.sites.models import Site
from django_celery_beat.admin import PeriodicTaskAdmin, PeriodicTask
from massadmin.massadmin import mass_change_selected
from nested_admin.nested import (
    NestedModelAdmin,
    NestedStackedInline, NestedTabularInline,
    NestedGenericStackedInline, NestedGenericTabularInline
)
from nested_admin.polymorphic import (
    NestedPolymorphicInlineSupportMixin,
    NestedStackedPolymorphicInline
)
from sass_processor.processor import sass_processor
from social_django.admin import UserSocialAuthOption, NonceOption, AssociationOption
from social_django.models import UserSocialAuth, Nonce, Association

from history.fields import HistoricDateTimeField, SourceFileField
from history.forms import HistoricDateWidget, SourceFileInput

PolymorphicInlineSupportMixin = NestedPolymorphicInlineSupportMixin
StackedPolymorphicInline = NestedStackedPolymorphicInline
GenericTabularInline = NestedGenericTabularInline
GenericStackedInline = NestedGenericStackedInline


class Admin(NestedModelAdmin):
    formfield_overrides = {
        HistoricDateTimeField: {'widget': HistoricDateWidget},
        SourceFileField: {'widget': SourceFileInput},
    }

    class Media:
        css = {
            'all': (
                'styles/base.css',
                'https://use.fontawesome.com/releases/v5.11.2/css/all.css',
                sass_processor('styles/mce.scss'),
                sass_processor('styles/admin.scss'),
            )
        }
        js = (
            '//ajax.googleapis.com/ajax/libs/jquery/3.4.1/jquery.min.js',  # jQuery
            '//maxcdn.bootstrapcdn.com/bootstrap/4.4.1/js/bootstrap.min.js',  # Bootstrap
            '//cdn.jsdelivr.net/npm/epubjs/dist/epub.min.js',  # EPub.JS
            'scripts/mce.js',
            'scripts/base.js'
        )


class StackedInline(NestedStackedInline):
    formfield_overrides = {
        HistoricDateTimeField: {'widget': HistoricDateWidget},
        SourceFileField: {'widget': SourceFileInput},
    }

    def get_fields(self, request, obj=None):
        fields = super().get_fields(request, obj)
        for field_name in ('page_number', 'end_page_number', 'notes', 'position'):
            if field_name in fields:
                fields.remove(field_name)
                fields.append(field_name)
        return fields


class TabularInline(NestedTabularInline):
    formfield_overrides = {
        HistoricDateTimeField: {'widget': HistoricDateWidget},
        SourceFileField: {'widget': SourceFileInput},
    }

    def get_fields(self, request, obj=None):
        fields = super().get_fields(request, obj)
        for field_name in ('page_number', 'end_page_number', 'notes', 'position'):
            if field_name in fields:
                fields.remove(field_name)
                fields.append(field_name)
        return fields


class AdminSite(BaseAdminSite):
    site_header = 'History administration'


admin_site = AdminSite(name='admin')
admin_site.add_action(mass_change_selected)


class CustomFlatPageAdmin(FlatPageAdmin):
    fieldsets = (
        (None, {'fields': ('url', 'title', 'content', 'sites')}),
        (('Advanced options',), {
            'classes': ('collapse', ),
            'fields': (
                'enable_comments',
                'registration_required',
                'template_name',
            ),
        }),
    )

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
# # response = requests.get('https://maps.googleapis.com/maps/api/geocode/json?address={0}&key={1}'.format(address, api_key)).json()
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


class ContentTypeAdmin(Admin):
    list_display = ['app_label', 'model', 'pk']
    list_filter = ('app_label',)
    readonly_fields = ['pk', 'app_label', 'model']
    ordering = ['app_label']


admin_site.register(Site)

admin_site.register(ContentType, ContentTypeAdmin)

admin_site.register(FlatPage, CustomFlatPageAdmin)

admin_site.register(PeriodicTask, PeriodicTaskAdmin)

admin_site.register(UserSocialAuth, UserSocialAuthOption)
admin_site.register(Nonce, NonceOption)
admin_site.register(Association, AssociationOption)

# admin_site.register(PeriodicTask, CustomPeriodicTaskAdmin)
# admin_site.register(IntervalSchedule)
# admin_site.register(CrontabSchedule)
# admin_site.register(TaskResult, TaskResultAdmin)
