from django.core.exceptions import ObjectDoesNotExist
from django.forms.models import ModelForm, model_to_dict

from apps.moderation.models.moderated_object import ModeratedObject


class BaseModeratedObjectForm(ModelForm):
    class Meta:
        exclude = '__all__'

    def __init__(self, *args, **kwargs):
        instance = kwargs.get('instance', None)

        if instance:
            try:
                if (
                    instance.moderated_object.status
                    in [
                        ModeratedObject.ModerationStatus.PENDING.value,
                        ModeratedObject.ModerationStatus.REJECTED.value,
                    ]
                    and not instance.moderated_object.moderator.visible_until_rejected
                ):
                    initial = model_to_dict(instance.moderated_object.changed_object)
                    kwargs.setdefault('initial', {})
                    kwargs['initial'].update(initial)
            except ObjectDoesNotExist:
                pass

        super().__init__(*args, **kwargs)
