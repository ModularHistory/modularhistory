from typing import Type

from django.contrib.contenttypes.models import ContentType

from apps.admin.model_admin import ExtendedModelAdmin
from apps.moderation.constants import ModerationStatus
from apps.moderation.forms import BaseModerationForm
from apps.moderation.models.change import Change
from apps.moderation.models.moderated_model.model import ModeratedModel


class ModeratedModelAdmin(ExtendedModelAdmin):
    """Admin for models requiring moderation."""

    admin_integration_enabled = True

    def get_form(self, request, obj=None, **kwargs):
        if obj and self.admin_integration_enabled:
            self.form = self.get_moderation_form(obj.__class__)
        return super().get_form(request, obj, **kwargs)

    def save_model(self, request, instance: 'ModeratedModel', form, change):
        if self.admin_integration_enabled:
            if instance.has_change_in_progress:
                change = instance.change_in_progress
                change.changed_object = instance
                change.save()
            else:
                change = Change.objects.create(
                    content_type=ContentType.objects.get_for_model(instance.__class__),
                    object_id=instance.pk,
                    moderation_status=ModerationStatus.PENDING,
                    changed_object=instance,
                )
        else:
            instance.save()

    def get_moderation_form(self, model_class: Type[ModeratedModel]):
        """Return the form to be used to propose changes to a moderated model instance."""

        class ModerationForm(BaseModerationForm):
            class Meta:
                model = model_class
                fields = '__all__'

        return ModerationForm
