"""Base classes for models that appear in ModularHistory search results."""

from modularhistory.fields import JSONField
from modularhistory.models.model import Model
from typing import Callable, Optional
from functools import wraps


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
        abstract = True

    def save(self, *args, **kwargs) -> None:
        """
        Saves the model instance to the database.

        By default, this method wipes the instance's computations. This way,
        when the instance is updated and saved from the admin (or via a script),
        properties will be recomputed when next accessed.  TODO: do better.
        """
        # By default, wipe the instance's computations when saving.
        wipe_computations = kwargs.pop('wipe_computations', True)
        if wipe_computations:
            self.computations = {}  # type: ignore
        super().save(*args, **kwargs)


def retrieve_or_compute(
    _func=None,
    *,
    attribute_name: Optional[str] = None,
    caster: Optional[Callable] = None,
):
    """
    `retrieve_or_compute` can be used as a decorator on methods/properties of
    ModelWithComputations. The decorator causes the attribute value to be retrieved from the
    JSON field if it is present; otherwise, the value is calculated (through the method/property
    logic) and stored to the JSON field (so that it can subsequently be retrieved without
    recalculation). The point is to reduce expensive computation and db queries.

    The optional decorator param `attribute_name` specifies the attribute name to search for
    in the JSON value. If it is not specified, the JSON value will be queried for a key with
    the same name as the decorated property name.

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

    def wrap(model_property):
        @wraps(model_property)
        def wrapped_property(model_instance: ModelWithComputations, *args, **kwargs):
            if isinstance(model_instance, ModelWithComputations):
                property_name = attribute_name or model_property.__name__
                property_value = model_instance.computations.get(property_name)
                if property_value is not None:
                    if caster and callable(caster):
                        property_value = caster(property_value)
                else:
                    property_value = model_property(model_instance, *args, **kwargs)
                    model_instance.computations[property_name] = property_value
                    # Specify `wipe_computations=False` to properly update the JSON value
                    model_instance.save(wipe_computations=False)
                return property_value
            raise TypeError(
                f'{model_instance.__class__} uses the @retrieve_or_compute decorator'
                f'on its `{model_property.__name__}` attribute but is not subclassed'
                f'from ModelWithComputations.'
            )

        return wrapped_property

    if _func is None:
        return wrap
    return wrap(_func)
