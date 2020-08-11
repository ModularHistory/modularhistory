# -*- coding: utf-8 -*-
"""
The manager class for use in the models.
"""
from __future__ import unicode_literals

from django.db import models

from polymorphic.query import PolymorphicQuerySet

__all__ = ("PolymorphicManager", "PolymorphicQuerySet")


class PolymorphicManager(models.Manager):
    """
    Manager for PolymorphicModel

    Usually not explicitly needed, except if a custom manager or
    a custom queryset class is to be used.
    """

    queryset_class = PolymorphicQuerySet

    @classmethod
    def from_queryset(cls, queryset_class, class_name=None):
        manager = super(PolymorphicManager, cls).from_queryset(
            queryset_class, class_name=class_name
        )
        # also set our version, Django uses _queryset_class
        manager.queryset_class = queryset_class
        return manager

    def get_queryset(self):
        qs = self.queryset_class(self.model, using=self._db, hints=self._hints)
        if self.model._meta.proxy:
            qs = qs.instance_of(self.model)
        return qs

    def __str__(self):
        return "%s (PolymorphicManager) using %s" % (
            self.__class__.__name__,
            self.queryset_class.__name__,
        )

    # Proxied methods
    def non_polymorphic(self):
        return self.all().non_polymorphic()

    def instance_of(self, *args):
        return self.all().instance_of(*args)

    def not_instance_of(self, *args):
        return self.all().not_instance_of(*args)

    def get_real_instances(self, base_result_objects=None):
        return self.all().get_real_instances(base_result_objects=base_result_objects)
