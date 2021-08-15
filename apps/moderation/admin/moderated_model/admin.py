from typing import TYPE_CHECKING, Any, Optional

from django.contrib.contenttypes.models import ContentType

from apps.admin.model_admin import ExtendedModelAdmin
from apps.moderation.constants import ModerationStatus
from apps.moderation.forms import SoftModificationForm
from apps.moderation.models.change import Change
from apps.moderation.models.contribution import ContentContribution
from apps.moderation.models.moderated_model.model import ModeratedModel

if TYPE_CHECKING:
    from django.forms import ModelForm
    from django.http import HttpRequest


class ModeratedModelAdmin(ExtendedModelAdmin):
    """Admin for models requiring moderation."""

    # If True, model instance changes are saved to a `Change` instance rather than
    # to the model instance, and the changes can then be moderated through the
    # `Change` admin. If False, the moderated model admin should function normally
    # and save changes directly to model instances.
    admin_integration_enabled = True

    def get_form(
        self,
        request: 'HttpRequest',
        obj: Optional[ModeratedModel] = None,
        **kwargs,
    ) -> 'ModelForm':
        """Return the form to be used in the admin to make changes to a model instance."""
        excluded_fields = self.exclude or []
        if obj and self.admin_integration_enabled:

            class _Form(SoftModificationForm):
                class Meta:
                    model = obj.__class__
                    exclude = excluded_fields

            return _Form
        return super().get_form(request, obj, **kwargs)

    def save_model(
        self,
        request: 'HttpRequest',
        instance: 'ModeratedModel',
        form: 'ModelForm',
        change: Any,
    ):
        """Save changes after the admin form is submitted."""
        # If admin integration for moderated models is active, save the changes to
        # the existing in-progress `Change` instance for the moderated model instance,
        # or create a new `Change` instance.
        if self.admin_integration_enabled:
            if instance.has_change_in_progress:
                _change = instance.change_in_progress
                ContentContribution.objects.create(
                    contributor=request.user,
                    change=_change,
                    content_before=_change.changed_object,
                    content_after=instance,
                )
                _change.changed_object = instance
                _change.save()
            else:
                _change: Change = Change.objects.create(
                    content_type=ContentType.objects.get_for_model(instance.__class__),
                    object_id=instance.pk,
                    moderation_status=ModerationStatus.PENDING,
                    changed_object=instance,
                )
                ContentContribution.objects.create(
                    contributor=request.user,
                    change=_change,
                    content_before=_change.unchanged_object,
                    content_after=instance,
                )
        # If admin integration for moderated models is not active, save the changes
        # directly to the model instance like normal.
        else:
            instance.save()
