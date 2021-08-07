import django
from django.contrib import admin
from django.contrib.contenttypes.models import ContentType
from django.forms.models import ModelForm
from django.urls import NoReverseMatch, reverse

from apps.admin import admin_site
from apps.moderation.diff import get_changes_between_models
from apps.moderation.filterspecs import RegisteredContentTypeListFilter
from apps.moderation.models import Change
from apps.moderation.models.moderated_model.model import ModeratedModel

from .actions import approve_objects, reject_objects, set_objects_as_pending


class ChangeAdmin(admin.ModelAdmin):
    date_hierarchy = 'created_date'
    list_display = ('content_object', 'content_type', 'created_date', 'moderation_status')
    list_filter = (('content_type', RegisteredContentTypeListFilter), 'moderation_status')
    change_form_template = 'moderation/changes/moderate_change.html'
    change_list_template = 'moderation/changes/changes_list.html'
    actions = [reject_objects, approve_objects, set_objects_as_pending]
    fieldsets = (('Moderation', {'fields': ('description',)}),)

    def get_actions(self, request):
        actions = super().get_actions(request)
        # Remove the delete_selected action if it exists
        try:
            del actions['delete_selected']
        except KeyError:
            pass
        return actions

    def content_object(self, obj):
        return str(obj.changed_object)

    def get_moderation_form(self, model_class):
        class ModerationForm(ModelForm):
            class Meta:
                model = model_class
                fields = '__all__'

        return ModerationForm

    def change_view(self, request, object_id, extra_context=None):
        change: Change = Change.objects.get(pk=object_id)
        object_after_change: ModeratedModel = change.changed_object
        object_before_change: ModeratedModel = change.unchanged_object
        changes = list(
            get_changes_between_models(
                object_before_change,
                object_after_change,
                [],  # TODO: moderator.fields_exclude,
                resolve_foreignkeys=True,
            ).values()
        )

        if request.POST:
            admin_form = self.get_form(request, change)(request.POST)
            if admin_form.is_valid():
                reason = admin_form.cleaned_data['reason']
                if 'approve' in request.POST:
                    change.approve(request.user, reason)
                elif 'reject' in request.POST:
                    change.reject(request.user, reason)

        content_type = ContentType.objects.get_for_model(object_after_change.__class__)
        try:
            object_admin_url = reverse(
                'admin:%s_%s_change' % (content_type.app_label, content_type.model),
                args=(object_after_change.pk,),
            )
        except NoReverseMatch:
            object_admin_url = None

        extra_context = {
            'changes': changes,
            'django_version': django.get_version()[:3],
            'object_admin_url': object_admin_url,
        }
        return super().change_view(request, object_id, extra_context=extra_context)


admin_site.register(Change, ChangeAdmin)