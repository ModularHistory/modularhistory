from django.core.exceptions import ObjectDoesNotExist
from django.forms.models import ModelForm, model_to_dict

from apps.moderation.models.change import Change


class BaseModerationForm(ModelForm):
    class Meta:
        exclude = '__all__'

    def __init__(self, *args, **kwargs):
        instance = kwargs.get('instance', None)

        if instance:
            try:
                if (
                    instance.moderation.status
                    in [
                        Change.ModerationStatus.PENDING.value,
                        Change.ModerationStatus.REJECTED.value,
                    ]
                    and not instance.moderation.moderator.visible_until_rejected
                ):
                    initial = model_to_dict(instance.moderation.changed_object)
                    kwargs.setdefault('initial', {})
                    kwargs['initial'].update(initial)
            except ObjectDoesNotExist:
                pass

        super().__init__(*args, **kwargs)
