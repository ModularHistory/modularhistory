from typing import List

from django.forms import ModelForm

from entities.models import Entity, Group, Idea, Person, Organization


class EntityForm(ModelForm):
    """TODO: add docstring."""

    class Meta:
        model = Entity
        exclude: List[str] = []

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.initial['type'] = self.instance.type


class OrganizationForm(ModelForm):
    """TODO: add docstring."""

    class Meta:
        model = Organization
        exclude: List[str] = []

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.initial['type'] = 'entities.organization'


class PersonForm(ModelForm):
    """TODO: add docstring."""

    class Meta:
        model = Person
        exclude: List[str] = ['parent_organization']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.initial['type'] = 'entities.person'

    # def clean_email(self):
    #     email = self.cleaned_data.get('email')
    #     if User.objects.filter(email=email).count() > 0:
    #         raise forms.ValidationError('An account with this email address has already been created.')
    #     return email


class GroupForm(ModelForm):
    """TODO: add docstring."""

    class Meta:
        model = Group
        exclude: List[str] = ['parent_organization']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.initial['type'] = 'entities.group'


class IdeaForm(ModelForm):
    """TODO: add docstring."""

    class Meta:
        model = Idea
        exclude: List[str] = []
