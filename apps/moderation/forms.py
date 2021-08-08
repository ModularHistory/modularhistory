from typing import TYPE_CHECKING, Optional

from django.forms.models import ModelForm, model_to_dict

if TYPE_CHECKING:
    from apps.moderation.models.moderated_model.model import ModeratedModel


class BaseModerationForm(ModelForm):
    class Meta:
        exclude = '__all__'

    def __init__(self, *args, **kwargs):
        instance: Optional['ModeratedModel'] = kwargs.get('instance', None)
        if instance:
            if instance.has_change_in_progress:
                initial = model_to_dict(instance.change_in_progress.changed_object)
                kwargs.setdefault('initial', {})
                kwargs['initial'].update(initial)

        super().__init__(*args, **kwargs)
