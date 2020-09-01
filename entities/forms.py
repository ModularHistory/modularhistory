from django.forms import ModelForm
from typing import List
from .models import Entity, Group, Idea, Person, Organization


class EntityForm(ModelForm):

    class Meta:
        model = Entity
        exclude: List[str] = []

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.initial['type'] = self.instance.type


class OrganizationForm(ModelForm):

    class Meta:
        model = Organization
        exclude = []

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.initial['type'] = 'entities.organization'


class PersonForm(ModelForm):

    class Meta:
        model = Person
        exclude = ['parent_organization']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.initial['type'] = 'entities.person'

    # def clean_email(self):
    #     email = self.cleaned_data.get('email')
    #     if User.objects.filter(email=email).count() > 0:
    #         raise forms.ValidationError('An account with this email address has already been created.')
    #     return email


class GroupForm(ModelForm):

    class Meta:
        model = Group
        exclude = ['parent_organization']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.initial['type'] = 'entities.group'


class IdeaForm(ModelForm):

    class Meta:
        model = Idea
        exclude = []
