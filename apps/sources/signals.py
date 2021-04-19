from django.db.models.signals import pre_delete, pre_save
from django.dispatch import receiver

from apps.sources.models import SourceContainment


# https://github.com/django/django/commit/9d104a21e20f9c5ec41d19fd919d0e808aa13dba
@receiver(pre_save, sender=SourceContainment)
def saving(sender, **kwargs):
    print(f'>>> pre_save sender: {sender.__class__.__name__}: {sender}: {kwargs}')


# https://github.com/django/django/commit/9d104a21e20f9c5ec41d19fd919d0e808aa13dba
@receiver(pre_delete, sender=SourceContainment)
def saving(sender, **kwargs):
    print(f'>>> pre_delete sender: {sender.__class__.__name__}: {sender}')
