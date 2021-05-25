from typing import Type, Union

from django.db import models
from django.utils.module_loading import import_string


class CustomManyToManyField(models.ManyToManyField):

    target_model: Union[str, Type[models.Model]]
    through_model: Union[str, Type[models.Model]]

    def __init__(self, **kwargs):
        to = kwargs.get('to', self.target_model)
        if to not in ('self', self.target_model):
            raise ValueError(f'{to} does not refer to `{self.target_model}`.')
        kwargs['to'] = to
        kwargs['related_name'] = kwargs.get('related_name', '%(class)s_set')
        kwargs['blank'] = kwargs.get('blank', True)
        through = kwargs.get('through')
        if isinstance(through, str):
            app_name, model_name = through.split('.')
            try:
                through_class = import_string(f'apps.{app_name}.models.{model_name}')
            except (ImportError, ModuleNotFoundError) as err:
                raise ModuleNotFoundError(
                    f'{err}.\n Hint: If the {app_name} app uses a `models` directory '
                    f'(rather than models.py), make sure the {model_name} class is '
                    f'imported in apps/{app_name}/models/__init__.py'
                )
        else:
            through_class = through
        if not issubclass(through_class, self.through_model):
            raise TypeError(f'{through} does not inherit from {self.through_model}.')
        super().__init__(**kwargs)
