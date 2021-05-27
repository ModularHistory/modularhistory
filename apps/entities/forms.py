from django.forms import ModelForm

from apps.entities.models import Deity, Entity, Group, Idea, Organization, Person

TYPE = 'type'


class EntityForm(ModelForm):
    """Form for entity admin."""

    class Meta:
        model = Entity
        exclude: list[str] = []

    def __init__(self, *args, **kwargs):
        """Construct the form for entity admin."""
        super().__init__(*args, **kwargs)
        self.initial[TYPE] = self.instance.type


class DeityForm(ModelForm):
    """Form for deity admin."""

    class Meta:
        model = Deity
        exclude: list[str] = []

    def __init__(self, *args, **kwargs):
        """Construct the form for entity admin."""
        super().__init__(*args, **kwargs)
        self.initial[TYPE] = 'entities.deity'


class OrganizationForm(ModelForm):
    """Form for organization admin."""

    class Meta:
        model = Organization
        exclude: list[str] = []

    def __init__(self, *args, **kwargs):
        """Construct the form for organization admin."""
        super().__init__(*args, **kwargs)
        self.initial[TYPE] = 'entities.organization'


class PersonForm(ModelForm):
    """Form for person admin."""

    class Meta:
        model = Person
        exclude: list[str] = []

    def __init__(self, *args, **kwargs):
        """Construct the form for person admin."""
        super().__init__(*args, **kwargs)
        self.initial[TYPE] = 'entities.person'


class GroupForm(ModelForm):
    """Form for group admin."""

    class Meta:
        model = Group
        exclude: list[str] = []

    def __init__(self, *args, **kwargs):
        """Construct the form for group admin."""
        super().__init__(*args, **kwargs)
        self.initial[TYPE] = 'entities.group'


class IdeaForm(ModelForm):
    """Form for idea admin."""

    class Meta:
        model = Idea
        exclude: list[str] = []
