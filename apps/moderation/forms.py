from typing import TYPE_CHECKING, Optional

from django.forms.models import ModelForm, model_to_dict

if TYPE_CHECKING:
    from apps.moderation.models.moderated_model.model import ModeratedModel


class SoftModificationForm(ModelForm):
    """
    Base form for suggesting changes to a moderated model instance.

    Changes are saved to a `Change` instance associated with the moderated model instance
    (to be moderated subsequently), rather than being saved directly to the model instance.
    """

    # Meta must be overridden by inheriting forms.
    class Meta:
        exclude = '__all__'

    def __init__(self, *args, **kwargs):
        """Construct the form."""
        instance: Optional['ModeratedModel'] = kwargs.get('instance', None)
        if instance:
            # Populate the form based on the moderated model instance's existing in-progress
            # change, if one exists; otherwise, let the form be populated based on the
            # current state of the moderated model instance.
            if instance.has_change_in_progress:
                initial = model_to_dict(instance.change_in_progress.changed_object)
                kwargs.setdefault('initial', {})
                kwargs['initial'].update(initial)
        super().__init__(*args, **kwargs)
