from typing import TYPE_CHECKING

from django.contrib import admin

from apps.admin import admin_site
from apps.admin.inlines import StackedInline
from apps.moderation.models import Change, ChangeSet

from .actions import approve_objects, reject_objects, set_objects_as_pending

if TYPE_CHECKING:
    from django.http.request import HttpRequest


class ChangesInline(StackedInline):
    """Inline admin for changes that comprise a change set."""

    model = Change
    fk_name = 'set'
    extra = 0

    # def get_formset(self, request: 'HttpRequest', obj: ChangeSet, **kwargs):
    #     """Return the formset for editing changes inline."""

    #     class FormSet(BaseInlineFormSet):
    #         """."""

    #     return FormSet


class ChangeSetAdmin(admin.ModelAdmin):
    actions = [reject_objects, approve_objects, set_objects_as_pending]
    # change_form_template = 'moderation/changesets/moderate_changeset.html'
    # change_list_template = 'moderation/changesets/changesets_list.html'
    date_hierarchy = 'created_date'
    fieldsets = (('Moderation', {'fields': ('description',)}),)
    inlines = [ChangesInline]
    list_display = ('created_date', 'moderation_status')
    list_filter = ('moderation_status',)

    def get_actions(self, request: 'HttpRequest'):
        """Return the batch actions available to the admin list view."""
        actions = super().get_actions(request)
        # Remove the delete_selected action if it exists.
        try:
            del actions['delete_selected']
        except KeyError:
            pass
        return actions

    def has_add_permission(self, request: 'HttpRequest', obj=None):
        """Return a boolean reflecting whether to include the "Add" button in the admin."""
        # Always return False; changesets should not be created manually.
        return False

    # def get_moderation_form(self, model_class):
    #     class ModerationForm(ModelForm):
    #         class Meta:
    #             model = model_class
    #             fields = '__all__'

    #     return ModerationForm

    # def change_view(self, request, object_id, extra_context=None):
    #     moderation = ChangeSet.objects.get(pk=object_id)
    #     changed_obj: ModeratedModel = moderation.object_after_change
    #     old_object = moderation.unchanged_object
    #     new_object = changed_obj
    #     changes = list(
    #         get_changes_between_models(
    #             old_object,
    #             new_object,
    #             moderator.fields_exclude,
    #             resolve_foreignkeys=moderator.resolve_foreignkeys,
    #         ).values()
    #     )

    #     if request.POST:
    #         admin_form = self.get_form(request, moderation)(request.POST)

    #         if admin_form.is_valid():
    #             reason = admin_form.cleaned_data['reason']
    #             if 'approve' in request.POST:
    #                 moderation.approve(request.user, reason)
    #             elif 'reject' in request.POST:
    #                 moderation.reject(request.user, reason)

    #     content_type = ContentType.objects.get_for_model(changed_obj.__class__)
    #     try:
    #         object_admin_url = reverse(
    #             'admin:%s_%s_change' % (content_type.app_label, content_type.model),
    #             args=(changed_obj.pk,),
    #         )
    #     except NoReverseMatch:
    #         object_admin_url = None

    #     extra_context = {
    #         'changes': changes,
    #         'django_version': django.get_version()[:3],
    #         'object_admin_url': object_admin_url,
    #     }
    #     return super().change_view(request, object_id, extra_context=extra_context)


admin_site.register(ChangeSet, ChangeSetAdmin)
