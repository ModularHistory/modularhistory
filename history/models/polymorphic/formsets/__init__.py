"""
This allows creating formsets where each row can be a different form type.
The logic of the formsets work similar to the standard Django formsets;
there are factory methods to construct the classes with the proper form settings.

The "parent" formset hosts the entire model and their child model.
For every child type, there is an :class:`PolymorphicFormSetChild` instance
that describes how to display and construct the child.
It's parameters are very similar to the parent's factory method.
"""
from .generic import (  # Can import generic here, as polymorphic already depends on the 'contenttypes' app.
    BaseGenericPolymorphicInlineFormSet,
    GenericPolymorphicFormSetChild,
    generic_polymorphic_inlineformset_factory,
)
from .models import (
    BasePolymorphicInlineFormSet,
    BasePolymorphicModelFormSet,
    PolymorphicFormSetChild,
    UnsupportedChildType,
    polymorphic_child_forms_factory,
    polymorphic_inlineformset_factory,
    polymorphic_modelformset_factory,
)

__all__ = (
    "BasePolymorphicModelFormSet",
    "BasePolymorphicInlineFormSet",
    "PolymorphicFormSetChild",
    "UnsupportedChildType",
    "polymorphic_modelformset_factory",
    "polymorphic_inlineformset_factory",
    "polymorphic_child_forms_factory",
    "BaseGenericPolymorphicInlineFormSet",
    "GenericPolymorphicFormSetChild",
    "generic_polymorphic_inlineformset_factory",
)
