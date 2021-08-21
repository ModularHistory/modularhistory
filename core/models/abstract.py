# https://stackoverflow.com/a/66888176/15369711

import abc

from django.db import models


class AbstractModelMeta(abc.ABCMeta, type(models.Model)):
    pass


class AbstractModel(models.Model, metaclass=AbstractModelMeta):
    class Meta:
        abstract = True
