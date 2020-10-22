from typing import List

from django.forms import ModelForm

from entities.models import Entity, Group, Idea, Person, Organization

TYPE = 'type'


class EntityForm(ModelForm):
    """Form for entity admin."""

    class Meta:
        model = Entity
        exclude: List[str] = []

    def __init__(self, *args, **kwargs):
        """Constructs the form for entity admin."""
        super().__init__(*args, **kwargs)
        self.initial[TYPE] = self.instance.type


class OrganizationForm(ModelForm):
    """Form for organization admin."""

    class Meta:
        model = Organization
        exclude: List[str] = []

    def __init__(self, *args, **kwargs):
        """Constructs the form for organization admin."""
        super().__init__(*args, **kwargs)
        self.initial[TYPE] = 'entities.organization'


class PersonForm(ModelForm):
    """Form for person admin."""

    class Meta:
        model = Person
        exclude: List[str] = ['parent_organization']

    def __init__(self, *args, **kwargs):
        """Constructs the form for person admin."""
        super().__init__(*args, **kwargs)
        self.initial[TYPE] = 'entities.person'


class GroupForm(ModelForm):
    """Form for group admin."""

    class Meta:
        model = Group
        exclude: List[str] = ['parent_organization']

    def __init__(self, *args, **kwargs):
        """Constructs the form for group admin."""
        super().__init__(*args, **kwargs)
        self.initial[TYPE] = 'entities.group'


class IdeaForm(ModelForm):
    """Form for idea admin."""

    class Meta:
        model = Idea
        exclude: List[str] = []
