from django.db.models.signals import post_save, pre_delete
from django.dispatch import receiver

from apps.sources import models


# https://github.com/django/django/commit/9d104a21e20f9c5ec41d19fd919d0e808aa13dba
@receiver(post_save, sender=models.SourceContainment)
def post_save_receiver(sender, **kwargs):
    # TODO: Verify citation HTML of the contained source is updated correctly.
    print(f'>>> pre_save: {sender.__class__.__name__}: {sender}: {kwargs}')


# https://github.com/django/django/commit/9d104a21e20f9c5ec41d19fd919d0e808aa13dba
@receiver(pre_delete, sender=models.SourceContainment)
def pre_delete_receiver(sender, **kwargs):
    # TODO: Verify citation HTML of previously related sources is updated correctly.
    print(f'>>> pre_delete: {sender.__class__.__name__}: {sender}: {kwargs}')
