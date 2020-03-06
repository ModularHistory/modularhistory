from django.forms import ModelForm

from .models import Group, Idea, Person, Organization


class OrganizationForm(ModelForm):

    class Meta:
        model = Organization
        exclude = []

    # def clean_email(self):
    #     email = self.cleaned_data.get('email')
    #     if User.objects.filter(email=email).count() > 0:
    #         raise forms.ValidationError('An account with this email address has already been created.')
    #     return email

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
