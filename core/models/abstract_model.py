from abc import ABCMeta

from django.db.models.base import ModelBase


class AbstractModelMeta(ABCMeta, ModelBase):
    """
    Meta class for abstract models.

    This meta class reconciles the meta classes of `django.db.models.Model` and
    `abc.ABC` so that the decorators provided by the `abc` module can be used by
    an abstract model. (Django's abstract models do not provide functionality
    comparable to ABC's "abstract methods." Also, Django models cannot directly
    inherit from `abc.ABC`, since this results in a metaclass conflict.)

    To use ABC with an abstract model, use `AbstractModelMeta` like so:
    ```
    from core.models import Model, AbstractModelMeta
    from abc import abstractmethod
    ...

    class MyAbstractModel(Model, metaclass=AbstractModelMeta):
        ...

        class Meta:
            abstract = True

        @property
        @abstractmethod
        def my_abstract_property(self):
            pass

        @abstractmethod
        def my_abstract_method(self):
            pass
    ```
    """
