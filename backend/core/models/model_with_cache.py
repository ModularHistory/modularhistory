"""Base classes for models that appear in ModularHistory search results."""

import json
import logging
from functools import wraps
from pprint import pformat
from typing import Callable, Optional, Union

from core.fields.json_field import JSONField
from core.models.model import ExtendedModel


class ModelWithCache(ExtendedModel):
    """A model with computed fields to be stored in JSON (to reduce db queries)."""

    cache = JSONField(null=True, blank=True, default=dict)

    # https://docs.djangoproject.com/en/dev/ref/models/options/#model-meta-options
    class Meta:
        abstract = True

    def save(self, *args, wipe_cache: bool = True, **kwargs) -> None:
        """
        Save the model instance to the database.

        By default, this method wipes the instance's computations. This way,
        when the instance is updated and saved from the admin (or via a script),
        properties will be recomputed when next accessed.  TODO: do better.
        """
        if wipe_cache:
            self.cache = {}  # type: ignore
        super().save(*args, **kwargs)  # type: ignore

    def pre_save(self):
        """Run any logic required before the instance is saved to the db."""

    def post_save(self):
        """Run any logic required after the instance is saved to the db."""

    @property
    def pretty_cache(self) -> str:
        """Return prettified JSON string of computations, for debugging/admin."""
        return json.dumps(self.cache, indent=4)


def store(
    _func=None,
    *,
    key: Optional[str] = None,
    caster: Optional[Callable] = None,
):
    """
    Cause a property of ModelWithCache to only be computed if necessary.

    If a previously computed value can be retrieved, return that value; otherwise,
    compute the property value and save it in the `computations` JSON field (so
    that it can subsequently be retrieved without recalculation).

    `store` can be used as a decorator on methods/properties of
    ModelWithCache. The point is to reduce expensive computation and db queries.

    The optional decorator param `attribute_name` specifies the attribute name to
    search for in the JSON value. If it is not specified, the JSON value will be
    queried for a key with the same name as the decorated property/method name.

    The optional decorator param `caster` specifies a callable to use to cast a value
    retrieved from JSON to the intended Python type (e.g., `format_html` to cast a
    string to SafeString).

    Examples:
    ``
    @property
    @store(attribute_name='html', caster=format_html)
    def html(self):
        html = self.related_object.html + '...'
        return html

    @store(attribute_name='categorization_string')
    def get_categorization_string(self, date: Optional[DateTime] = None):
        categorization_string = ...
        return categorization_string
    ``

    For a primer on Python decorators, see:
    https://realpython.com/primer-on-python-decorators/
    """

    def wrap(model_property):  # noqa: ANN201,WPS430
        @wraps(model_property)  # noqa: ANN201,WPS430
        def wrapped_property(
            model_instance: Union[ModelWithCache, ExtendedModel], *args, **kwargs
        ):
            # Avoid recursion errors when creating new model instances
            if model_instance.pk:
                if isinstance(model_instance, ModelWithCache):
                    property_name = key or model_property.__name__
                    # If the computation result is None, the key will be added to the
                    # JSON but its value will be None. Therefore, to check for a
                    # previous computation result, we must explicitly check for the
                    # key in the JSON rather than relying on `get`.
                    if property_name in model_instance.cache:
                        saved_value = model_instance.cache[property_name]
                        property_value = '' if saved_value is None else saved_value
                        if caster and callable(caster):
                            property_value = caster(property_value)
                    else:
                        property_value = model_property(model_instance, *args, **kwargs)
                        model_instance.cache[property_name] = property_value
                        logging.info(
                            # Do not use the model instance's __str__ method;
                            # it may cause a recursion error.
                            f'Saving computed field `{property_name}` to '
                            f'{model_instance.__class__.__name__} ({model_instance.pk}) '
                            f'with value: {pformat(property_value)}'
                        )
                        # Specify `wipe_cache=False` to properly update the JSON value
                        model_instance.save(wipe_cache=False, moderate=False)  # type: ignore
                    return property_value
                logging.error(
                    f'{model_instance.__class__.__name__} uses @store '
                    f'on its `{model_property.__name__}` attribute '
                    f'but is not subclassed from ModelWithCache.'
                )
            return None

        return wrapped_property

    if _func is None:
        return wrap
    return wrap(_func)
