from celery import shared_task
from django.db import models, transaction
from django.utils import timezone
from django_elasticsearch_dsl.apps import DEDConfig
from django_elasticsearch_dsl.registries import registry
from django_elasticsearch_dsl.signals import BaseSignalProcessor

from core.utils import models as utils


class CelerySignalProcessor(BaseSignalProcessor):
    """
    Celery signal processor for ElasticSearch DSL.

    Allows automatic updates on the index as delayed background tasks using Celery.

    Note: Processing deletes is still handled synchronously, since by the time the Celery
    worker would pick up the delete job, the model instance would already be deleted.
    """

    NO_INDEXED_AT_FIELD = -1

    def handle_save(self, sender, instance, **kwargs):
        if not DEDConfig.autosync_enabled():
            return

        if instance.__class__ not in registry.get_models():
            return

        serialized_sender = utils.serialize_model(sender)
        serialized_instance = utils.serialize_model_instance(instance)
        return self.async_handle_save.apply_async(
            (
                serialized_sender,
                serialized_instance,
                getattr(instance, 'indexed_at', self.NO_INDEXED_AT_FIELD),
            ),
            countdown=10,
        )

    @staticmethod
    def perform_elastic_update(instance):
        registry.update(instance)
        registry.update_related(instance)

    @shared_task(bind=True)
    def async_handle_save(self, sender, instance, indexed_at):
        deserialized_sender = utils.deserialize_model(sender)  # noqa

        if indexed_at == CelerySignalProcessor.NO_INDEXED_AT_FIELD:
            instance = utils.deserialize_model_instance(instance)
            CelerySignalProcessor.perform_elastic_update(instance)
            return

        with transaction.atomic():
            time_of_retrieval = timezone.now()
            instance = utils.deserialize_model_instance(instance, select_for_update=True)
            if utils.has_been_indexed_since(instance, timestamp=indexed_at):
                return

            CelerySignalProcessor.perform_elastic_update(instance)
            utils.update_indexed_at(instance, timestamp=time_of_retrieval)

    def setup(self):
        """Set up listeners."""
        models.signals.post_save.connect(self.handle_save)
        models.signals.post_delete.connect(self.handle_delete)

        # Manage related objects update.
        models.signals.m2m_changed.connect(self.handle_m2m_changed)
        models.signals.pre_delete.connect(self.handle_pre_delete)

    def teardown(self):
        """Destroy listeners."""
        models.signals.post_save.disconnect(self.handle_save)
        models.signals.post_delete.disconnect(self.handle_delete)
        models.signals.m2m_changed.disconnect(self.handle_m2m_changed)
        models.signals.pre_delete.disconnect(self.handle_pre_delete)
