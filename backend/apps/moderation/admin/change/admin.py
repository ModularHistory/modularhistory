from typing import TYPE_CHECKING, Optional

from django.contrib.admin import ModelAdmin
from django.contrib.contenttypes.models import ContentType
from django.urls import NoReverseMatch, reverse

from apps.admin.admin_site import admin_site
from apps.admin.list_filters.autocomplete_filter import ManyToManyAutocompleteFilter
from apps.admin.list_filters.type_filter import ContentTypeFilter
from apps.moderation.diff import get_field_changes
from apps.moderation.models import Change
from apps.moderation.models.moderated_model.model import ModeratedModel

from .actions import approve_objects, reject_objects, set_objects_as_pending

if TYPE_CHECKING:
    from django.http.request import HttpRequest

    from apps.moderation.models.change.queryset import ChangeQuerySet


class ContributorFilter(ManyToManyAutocompleteFilter):
    """Filter for changes to which a specific contributor has contributed."""

    title = 'contributor'
    field_name = 'contributors'
    _parameter_name = 'contributors__pk__exact'
    m2m_cls = 'users.User'

    def get_autocomplete_url(self, request: 'HttpRequest', model_admin: ModelAdmin) -> str:
        """Return the URL used for topic autocompletion."""
        return reverse('admin:user_search')


class ChangeAdmin(ModelAdmin):
    """
    Admin for changes proposed to moderated model instances.

    This enables users with moderation privileges to accept or reject changes.
    """

    date_hierarchy = 'created_date'
    list_display = (
        'content_object',
        'content_type',
        'updated_date',
        'created_date',
        'moderation_status',
        'n_remaining_approvals_required',
    )
    list_filter = (
        ContentTypeFilter,
        'n_remaining_approvals_required',
        'moderation_status',
        ContributorFilter,
        'merged_date',
    )
    ordering = [
        'moderation_status',
        'n_remaining_approvals_required',
        '-updated_date',
        'created_date',
    ]
    search_fields = ['changed_object']
    change_form_template = 'moderation/changes/moderate_change.html'
    change_list_template = 'moderation/changes/changes_list.html'
    actions = [reject_objects, approve_objects, set_objects_as_pending]
    fieldsets = (('Moderation', {'fields': ('description',)}),)
    exclude_relations = True

    def get_queryset(self, request: 'HttpRequest') -> 'ChangeQuerySet':
        queryset = super().get_queryset(request)
        if self.exclude_relations:
            queryset = queryset.filter(parent__isnull=True)  # TODO
        return queryset

    def get_actions(self, request: 'HttpRequest'):
        """Return the bulk actions available to the admin."""
        actions = super().get_actions(request)
        # Remove the delete_selected action if it exists.
        try:
            del actions['delete_selected']
        except KeyError:
            pass
        return actions

    # https://docs.djangoproject.com/en/dev/ref/contrib/admin/#django.contrib.admin.ModelAdmin.change_view
    def change_view(
        self,
        request: 'HttpRequest',
        object_id: int,
        extra_context: Optional[dict] = None,
    ):
        """Return the Django view for the change moderation page."""
        change: Change = Change.objects.get(pk=object_id)
        object_after_change: ModeratedModel = change.changed_object
        object_before_change: ModeratedModel = change.unchanged_object
        changes = list(
            get_field_changes(
                change,
                excluded_fields=object_before_change.Moderation.excluded_fields,
                resolve_foreignkeys=True,
            ).values()
        )
        if request.POST:
            admin_form = self.get_form(request, change)(request.POST)
            if admin_form.is_valid():
                reason = admin_form.cleaned_data.get('reason')
                if 'force' in request.POST:
                    change.approve(moderator=request.user, reason=reason, force=True)
                if 'approve' in request.POST:
                    change.approve(moderator=request.user, reason=reason)
                elif 'reject' in request.POST:
                    change.reject(moderator=request.user, reason=reason)
        content_type = ContentType.objects.get_for_model(object_after_change.__class__)
        try:
            object_admin_url = reverse(
                f'admin:{content_type.app_label}_{content_type.model}_change',
                args=(object_after_change.pk,),
            )
        except NoReverseMatch:
            object_admin_url = None
        extra_context = {
            'changes': changes,
            'object_admin_url': object_admin_url,
        }
        return super().change_view(request, object_id, extra_context=extra_context)


admin_site.register(Change, ChangeAdmin)
