import logging

import magic
from crispy_forms.helper import FormHelper
from crispy_forms.layout import HTML, Field, Layout, Submit
from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserCreationForm as BaseUserCreationForm

from apps.users.admin import EMAIL_FIELD, USERNAME_FIELD

User = get_user_model()

DEFAULT_FIELD_CLASSES = 'form-control mb-4'


class UserCreationForm(BaseUserCreationForm):
    """Admin form for user creation."""

    class Meta:
        model = User
        exclude = ()


class RegistrationForm(UserCreationForm):
    """Crispy registration form."""

    class Meta:
        model = User
        fields = ['first_name', 'last_name', USERNAME_FIELD, EMAIL_FIELD]

    def __init__(self, *args, **kwargs):
        """Construct a registration form."""
        super().__init__(*args, **kwargs)
        # https://django-crispy-forms.readthedocs.io/en/latest/form_helper.html
        self.helper = FormHelper()
        self.helper.field_class = ''
        self.helper.form_id = 'registrationForm'
        self.helper.form_class = 'text-center border border-light p-5'
        self.helper.form_method = 'post'
        self.helper.form_action = '/register'
        self.helper.label_class = 'hidden'
        self.helper.layout = Layout(
            HTML('<p class="h4 mb-4">Register account</p>'),
            HTML('<div class="form-row mb-4"><div class="col">'),
            Field('first_name', placeholder='First name'),
            HTML('</div><div class="col">'),
            Field('last_name', placeholder='Last name'),
            HTML('</div></div>'),
            Field(
                EMAIL_FIELD,
                css_class=DEFAULT_FIELD_CLASSES,
                placeholder='Email address',
            ),
            Field(USERNAME_FIELD, css_class=DEFAULT_FIELD_CLASSES, placeholder='Username'),
            Field('password1', css_class=DEFAULT_FIELD_CLASSES, placeholder='Password'),
            Field(
                'password2',
                css_class=DEFAULT_FIELD_CLASSES,
                placeholder='Confirm password',
            ),
            Submit('submit', 'Create account', css_class='btn btn-info btn-block my-4'),
            HTML('<p>Already have an account? <a href="api/auth/signin">Sign in</a></p>'),
        )

    def clean_email(self):
        """Clean the email field value."""
        email = self.cleaned_data.get(EMAIL_FIELD)
        if not self.cleaned_data.get(USERNAME_FIELD):
            self.cleaned_data[USERNAME_FIELD] = email
        if email and User.objects.filter(email=email).exists():
            raise forms.ValidationError(
                'An account with this email address has already been created.'
            )
        return email

    def clean_username(self):
        """Prepare the username field value to be saved."""
        email = self.cleaned_data.get(EMAIL_FIELD)
        username = self.cleaned_data.get(USERNAME_FIELD) or email
        if email:
            if User.objects.filter(email=email).count() > 0:
                raise forms.ValidationError(
                    'An account with this email address already exists.'
                )
        if username:
            if User.objects.filter(username=username).count() > 0:
                raise forms.ValidationError(
                    'An account with this username has already been created.'
                )
        return username

    def clean_first_name(self):
        """Prepare the first_name field value to be saved."""
        return self.cleaned_data.get('first_name').title()

    def clean_last_name(self):
        """Prepare the last_name field value to be saved."""
        return self.cleaned_data.get('last_name').title()

    def clean(self):
        """Prepare field values to be saved."""
        cleaned_data = super().clean()
        if cleaned_data.get('password1') != cleaned_data.get('password2'):
            raise forms.ValidationError('Your passwords need to match. Please try again.')
        return cleaned_data


class PictureForm(forms.Form):
    """Form for submitting or updating a profile picture."""

    form_id = 'picture-form'
    action = '/users/profile.picture/'
    method = 'POST'
    submit = 'Upload'
    is_ajax = True

    picture = forms.ImageField(label='Profile picture', required=False)

    def clean_picture(self):
        """Prepare the picture to be saved."""
        picture = self.cleaned_data.get('picture', False)
        picture.file.seek(0)
        mime = magic.from_buffer(picture.file.getvalue(), mime=True)
        logging.debug(f'Picture mime type is {mime}.')
        if mime not in ('image/png', 'image/jpeg', 'image/jpg'):
            raise forms.ValidationError('The file type must be JPG or PNG.')
        return picture
