from typing import TYPE_CHECKING, Optional, Union

from django.contrib.contenttypes.models import ContentType
from django.db.models.base import Model
from django.utils import timezone
from image_cropping import ImageCropWidget

from apps.admin.list_filters.boolean_filters import HasValueFilter
from apps.admin.model_admin import ExtendedModelAdmin
from apps.admin.widgets.historic_date_widget import HistoricDateWidget
from apps.moderation.constants import ModerationStatus
from apps.moderation.forms import SoftModificationForm
from apps.moderation.models.change.model import Change
from apps.moderation.models.changeset.model import ChangeSet
from apps.moderation.models.moderated_model.model import ModeratedModel
from core.models.relations.moderated import ModeratedRelation

if TYPE_CHECKING:
    from django.forms import ModelForm
    from django.forms.formsets import BaseFormSet as FormSet
    from django.http import HttpRequest


class DeletedFilter(HasValueFilter):
    """Filter for deleted objects."""

    title = parameter_name = field = 'deleted'


class ModeratedModelAdmin(ExtendedModelAdmin):
    """Admin for models requiring moderation."""

    # If True, model instance changes are saved to a `Change` instance rather than
    # to the model instance, and the changes can then be moderated through the
    # `Change` admin. If False, the moderated model admin should function normally
    # and save changes directly to model instances.
    admin_integration_enabled = True

    list_filter = [DeletedFilter]

    class Media(ExtendedModelAdmin.Media):
        """Include admin CSS and JS."""

    def get_model_cls(
        self, obj: Optional['ModeratedModel'] = None
    ) -> Optional[type['ModeratedModel']]:
        """Return the class of the moderated model."""
        if obj is None:
            return getattr(self, 'model', None)
        return obj.__class__  # type: ignore

    def get_exclude(
        self, request: 'HttpRequest', obj: Optional['ModeratedModel']
    ) -> list[str]:
        """Return the fields to be excluded from the admin form."""
        excluded_fields = super().get_exclude(request, obj=obj)
        if self.admin_integration_enabled:
            model_cls = self.get_model_cls(obj)
            if model_cls:
                excluded_fields = list(
                    {*model_cls.Moderation.excluded_fields, *excluded_fields}
                )
        return excluded_fields

    def get_form(
        self,
        request: 'HttpRequest',
        obj: Optional[ModeratedModel] = None,
        **kwargs,
    ) -> 'ModelForm':
        """Return the form to be used to make changes to a model instance."""
        model_cls = self.get_model_cls(obj)
        if model_cls and self.admin_integration_enabled:
            excluded_fields = self.get_exclude(request=request, obj=obj)

            class _Form(SoftModificationForm):
                class Meta:
                    model = model_cls
                    exclude = excluded_fields
                    widgets = {
                        'date': HistoricDateWidget,
                        'end_date': HistoricDateWidget,
                        'image': ImageCropWidget,
                    }

            return _Form
        return super().get_form(request, obj, **kwargs)

    def save_model(
        self,
        request: 'HttpRequest',
        instance: 'ModeratedModel',
        form: 'ModelForm',
        change: bool,
    ):
        """Save changes after the admin form is submitted."""
        # If admin integration for moderated models is active, save the changes to
        # a `Change` instance for the moderated model instance.
        if self.admin_integration_enabled:
            instance.save_change(contributor=request.user)
        # If admin integration for moderated models is not active, save the changes
        # directly to the model instance like normal.
        else:
            instance.save()

    def save_formset(
        self,
        request: 'HttpRequest',
        form: 'ModelForm',
        formset: 'FormSet',
        change: bool,
    ):
        """Save changes to related objects managed through inline admin forms."""
        instance: 'ModeratedModel' = form.instance
        # If admin integration for moderated models is active, save the changes to
        # the existing in-progress `Change` instance for the moderated model instance,
        # or create a new `Change` instance.
        if self.admin_integration_enabled:
            formset.save(commit=False)
            # relations_queryset: 'QuerySet' = formset.queryset
            parent_change: Change = (
                instance.change_in_progress
                if instance.has_change_in_progress
                else Change.objects.create(
                    content_type=ContentType.objects.get_for_model(instance.__class__),
                    object_id=instance.pk,
                    moderation_status=ModerationStatus.PENDING,
                    changed_object=instance,
                )
            )
            change_set: ChangeSet = parent_change.set or ChangeSet.objects.create()
            relation: Union['ModeratedRelation', Model]
            for relation in formset.new_objects:
                relation.save_change(
                    contributor=request.user,
                    set=change_set,
                    parent_change=parent_change,
                )
            for relation, _changed_fields in formset.changed_objects:
                relation.save_change(
                    contributor=request.user,
                    set=change_set,
                    parent_change=parent_change,
                )
            for relation in formset.deleted_objects:
                if isinstance(relation, ModeratedRelation):
                    relation.deleted = timezone.now()
                    relation.save_change(
                        contributor=request.user,
                        set=change_set,
                        parent_change=parent_change,
                    )
                else:
                    relation.delete()
        else:
            super().save_formset(request, form, formset, change)
