"""Base classes for models that appear in ModularHistory search results."""

import json
import logging
from functools import wraps
from typing import Callable, Optional

from modularhistory.fields import JSONField
from modularhistory.models.model import Model


class ModelWithComputations(Model):
    """
    A model with computed fields to be stored in JSON (to reduce db queries).

    Ideally, this class would be a mixin, but do to Django's model magic,
    it must be defined as an abstract model class.
    """

    computations = JSONField(null=True, blank=True, default=dict)

    class FieldNames(Model.FieldNames):
        computations = 'computations'

    class Meta:
        """
        Meta options for ModelWithComputations.

        See https://docs.djangoproject.com/en/3.1/ref/models/options/#model-meta-options.
        """

        abstract = True

    def save(self, *args, **kwargs) -> None:
        """
        Save the model instance to the database.

        By default, this method wipes the instance's computations. This way,
        when the instance is updated and saved from the admin (or via a script),
        properties will be recomputed when next accessed.  TODO: do better.
        """
        # By default, wipe the instance's computations when saving.
        wipe_computations = kwargs.pop('wipe_computations', True)
        if wipe_computations:
            self.computations = {}  # type: ignore
        super().save(*args, **kwargs)

    @property
    def pretty_computations(self) -> str:
        """Return prettified JSON string of computations, for debugging/admin."""
        return json.dumps(self.computations, indent=4)


def retrieve_or_compute(
    _func=None,
    *,
    attribute_name: Optional[str] = None,
    caster: Optional[Callable] = None,
):
    """
    Cause a property of ModelWithComputations to only be computed if necessary.

    If a previously computed value can be retrieved, return that value; otherwise,
    compute the property value and save it in the `computations` JSON field (so
    that it can subsequently be retrieved without recalculation).

    `retrieve_or_compute` can be used as a decorator on methods/properties of
    ModelWithComputations. The point is to reduce expensive computation and db queries.

    The optional decorator param `attribute_name` specifies the attribute name to
    search for in the JSON value. If it is not specified, the JSON value will be
    queried for a key with the same name as the decorated property/method name.

    The optional decorator param `caster` specifies a callable to use to cast a value
    retrieved from JSON to the intended Python type (e.g., `format_html` to cast a
    string to SafeString).

    Examples:
    ``
    @property
    @retrieve_or_compute(attribute_name='html', caster=format_html)
    def html(self):
        html = self.related_object.html + '...'
        return html

    @retrieve_or_compute(attribute_name='categorization_string')
    def get_categorization_string(self, date: Optional[DateTime] = None):
        categorization_string = ...
        return categorization_string
    ``

    For a primer on Python decorators, see:
    https://realpython.com/primer-on-python-decorators/
    """

    def wrap(model_property):  # noqa: WPS430
        @wraps(model_property)  # noqa: WPS430
        def wrapped_property(model_instance: ModelWithComputations, *args, **kwargs):
            # Avoid recursion errors when creating new model instances
            if model_instance.pk:
                if isinstance(model_instance, ModelWithComputations):
                    property_name = attribute_name or model_property.__name__
                    # If the computation result is None, the key will be added to the
                    # JSON but its value will be None. Therefore, to check for a
                    # previous computation result, we must explicitly check for the
                    # key in the JSON rather than relying on `get`.
                    if property_name in model_instance.computations:
                        saved_value = model_instance.computations[property_name]
                        property_value = '' if saved_value is None else saved_value
                        if caster and callable(caster):
                            property_value = caster(property_value)
                    else:
                        property_value = model_property(model_instance, *args, **kwargs)
                        model_instance.computations[property_name] = property_value
                        logging.info(
                            # Do not use the model instance's __str__ method;
                            # it may cause a recursion error.
                            f'>>> Saving computed field `{property_name}` to '
                            f'{model_instance.__class__.__name__} ({model_instance.pk}) '
                            f'with value: {property_value}'
                        )
                        # Specify `wipe_computations=False` to properly update the JSON value
                        model_instance.save(wipe_computations=False)
                    return property_value
                logging.error(  # type: ignore
                    f'{model_instance.__class__.__name__} uses @retrieve_or_compute '
                    f'on its `{model_property.__name__}` attribute '
                    f'but is not subclassed from ModelWithComputations.'
                )
            return None

        return wrapped_property

    if _func is None:
        return wrap
    return wrap(_func)
