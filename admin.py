from django.contrib.admin import AdminSite
# from django.contrib.flatpages.admin import FlatPageAdmin
# from django.contrib.flatpages.models import FlatPage
# from django.contrib.sites.models import Site
# from django.utils.translation import gettext_lazy as _
# from django_celery_beat.models import PeriodicTask, PeriodicTasks, CrontabSchedule, IntervalSchedule, SolarSchedule
# from django_celery_beat.admin import PeriodicTaskAdmin, PeriodicTaskForm
# from django_celery_results.models import TaskResult
# from django_celery_results.admin import TaskResultAdmin


class HistoryAdminSite(AdminSite):
    site_header = 'History administration'


admin_site = HistoryAdminSite(name='admin')


# class CustomFlatPageAdmin(FlatPageAdmin):
#     fieldsets = (
#         (None, {'fields': ('url', 'title', 'content', 'sites')}),
#         (('Advanced options'), {
#             'classes': ('collapse', ),
#             'fields': (
#                 'enable_comments',
#                 'registration_required',
#                 'template_name',
#             ),
#         }),
#     )

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

# admin_site.register(Site)
# admin_site.register(FlatPage, CustomFlatPageAdmin)
# admin_site.register(PeriodicTask, CustomPeriodicTaskAdmin)
# admin_site.register(IntervalSchedule)
# admin_site.register(CrontabSchedule)
# admin_site.register(TaskResult, TaskResultAdmin)
