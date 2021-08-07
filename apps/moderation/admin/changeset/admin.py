import django
from django.contrib import admin
from django.contrib.contenttypes.models import ContentType
from django.forms.models import ModelForm
from django.urls import NoReverseMatch, reverse

from apps.admin import admin_site
from apps.moderation.diff import get_changes_between_models
from apps.moderation.models import ChangeSet
from apps.moderation.models.moderated_model.model import ModeratedModel

from .actions import approve_objects, reject_objects, set_objects_as_pending


class ChangeSetAdmin(admin.ModelAdmin):
    date_hierarchy = 'created_date'
    list_display = ('created_date', 'moderation_status')
    list_filter = ('moderation_status',)
    change_form_template = 'moderation/changesets/moderate_changeset.html'
    change_list_template = 'moderation/changesets/changesets_list.html'
    actions = [reject_objects, approve_objects, set_objects_as_pending]
    fieldsets = (('Object moderation', {'fields': ('description',)}),)

    def get_actions(self, request):
        """Return the batch actions available to the admin list view."""
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
        moderation = ChangeSet.objects.get(pk=object_id)
        changed_obj: ModeratedModel = moderation.changed_object
        old_object = moderation.unchanged_object
        new_object = changed_obj
        changes = list(
            get_changes_between_models(
                old_object,
                new_object,
                moderator.fields_exclude,
                resolve_foreignkeys=moderator.resolve_foreignkeys,
            ).values()
        )

        if request.POST:
            admin_form = self.get_form(request, moderation)(request.POST)

            if admin_form.is_valid():
                reason = admin_form.cleaned_data['reason']
                if 'approve' in request.POST:
                    moderation.approve(request.user, reason)
                elif 'reject' in request.POST:
                    moderation.reject(request.user, reason)

        content_type = ContentType.objects.get_for_model(changed_obj.__class__)
        try:
            object_admin_url = reverse(
                'admin:%s_%s_change' % (content_type.app_label, content_type.model),
                args=(changed_obj.pk,),
            )
        except NoReverseMatch:
            object_admin_url = None

        extra_context = {
            'changes': changes,
            'django_version': django.get_version()[:3],
            'object_admin_url': object_admin_url,
        }
        return super().change_view(request, object_id, extra_context=extra_context)


admin_site.register(ChangeSet, ChangeSetAdmin)
