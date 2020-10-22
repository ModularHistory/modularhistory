from typing import List

from django import forms
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import Group, Permission
from social_django.admin import AssociationOption, NonceOption, UserSocialAuthOption
from social_django.models import Association, Nonce, UserSocialAuth

from account.models import User
# from account.forms import UserCreationForm #  UserChangeForm
from admin import TabularInline, admin_site

EMAIL_FIELD = 'email'
USERNAME_FIELD = 'username'
PASSWORD_FIELD = 'password'  # noqa: S105
FIRST_NAME_FIELD = 'first_name'
LAST_NAME_FIELD = 'last_name'
FORCE_PASSWORD_CHANGE_FIELD = 'force_password_change'  # noqa: S105
IS_SUPERUSER_FIELD = 'is_superuser'
AVATAR_FIELD = 'avatar'

PERMISSIONS_LABEL = 'Permissions'

FIELDS_KEY = 'fields'
CLASSES_KEY = 'classes'

MAX_EMAIL_LENGTH: int = 100
MAX_NAME_LENGTH: int = 100

DEFAULT_WIDGET_ATTRIBUTES = {'class': 'form-control'}


class UserCreationForm(forms.ModelForm):
    """
    A form for creating new users.

    Includes all the required fields, plus a repeated password.
    """

    username = forms.CharField(required=False, widget=forms.HiddenInput())
    email = forms.EmailField(
        label='Email',
        required=True,
        max_length=MAX_EMAIL_LENGTH,
        widget=forms.TextInput(attrs=DEFAULT_WIDGET_ATTRIBUTES)
    )
    first_name = forms.CharField(
        label='First Name',
        required=False,
        max_length=MAX_NAME_LENGTH,
        widget=forms.TextInput(attrs=DEFAULT_WIDGET_ATTRIBUTES)
    )
    last_name = forms.CharField(
        label='Last Name',
        required=False,
        max_length=MAX_NAME_LENGTH,
        widget=forms.TextInput(attrs=DEFAULT_WIDGET_ATTRIBUTES)
    )
    password1 = forms.CharField(label='Password', widget=forms.PasswordInput)
    password2 = forms.CharField(label='Password confirmation', widget=forms.PasswordInput)
    force_password_change = forms.BooleanField(
        help_text='Prompt user to change password upon first login',
        required=False,
        initial=True
    )
    groups = forms.ModelMultipleChoiceField(
        label='Groups',
        required=False,
        queryset=Group.objects.all(),
        widget=forms.CheckboxSelectMultiple(attrs=DEFAULT_WIDGET_ATTRIBUTES)
    )
    permissions = forms.ModelMultipleChoiceField(
        label=PERMISSIONS_LABEL,
        required=False,
        queryset=Permission.objects.all(),
        help_text=(
            'Specifying permissions individually is not necessary '
            'if the user belongs to a group to which those permissions are already allocated.'
        )
    )

    class Meta:
        model = User
        fields = [
            EMAIL_FIELD,
            PASSWORD_FIELD,
            FIRST_NAME_FIELD,
            LAST_NAME_FIELD,
            AVATAR_FIELD,
            IS_SUPERUSER_FIELD,
            FORCE_PASSWORD_CHANGE_FIELD
        ]

    def clean_email(self):
        """Cleans the email field value."""
        email = self.cleaned_data.get(EMAIL_FIELD)
        if User.objects.filter(email=email).count() > 0:
            raise forms.ValidationError('An account with this email address has already been created.')
        return email

    def clean_username(self):
        """Cleans the username field value."""
        username = self.cleaned_data.get(USERNAME_FIELD) or self.cleaned_data.get(EMAIL_FIELD)
        if User.objects.filter(username=username).count() > 0:
            raise forms.ValidationError('An account with this username has already been created.')
        return username

    def clean(self):
        """Prepares the input values to be saved."""
        # Check that the two password entries match
        password1 = self.cleaned_data.get('password1')
        password2 = self.cleaned_data.get('password2')
        if password1 and password2 and password1 != password2:
            raise forms.ValidationError('Passwords do not match.')
        return password2

    def save(self, commit=True):
        """TODO: add docstring."""
        # Save the provided password in hashed format
        user = super(UserCreationForm, self).save(commit=False)
        user.username = self.cleaned_data.get(USERNAME_FIELD) or self.cleaned_data.get(EMAIL_FIELD)
        user.set_password(self.cleaned_data['password1'])
        if commit:
            user.save()
        return user


class UserChangeForm(forms.ModelForm):
    """
    A form for updating users.

    Includes all the fields on the user, but replaces the password field
    with the admin's password hash display field.
    """

    username = forms.CharField(required=False, widget=forms.HiddenInput())
    email = forms.EmailField(
        label='Email',
        required=True,
        max_length=MAX_EMAIL_LENGTH,
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    first_name = forms.CharField(
        label='First Name',
        required=False,
        max_length=MAX_NAME_LENGTH,
        widget=forms.TextInput(attrs=DEFAULT_WIDGET_ATTRIBUTES)
    )
    last_name = forms.CharField(
        label='Last Name',
        required=False,
        max_length=MAX_NAME_LENGTH,
        widget=forms.TextInput(attrs=DEFAULT_WIDGET_ATTRIBUTES)
    )
    force_password_change = forms.BooleanField(label='Force password change', required=False)
    locked = forms.BooleanField(label='Locked', required=False)
    groups = forms.ModelMultipleChoiceField(
        label='Groups',
        required=False,
        queryset=Group.objects.all(),
        widget=forms.CheckboxSelectMultiple(attrs=DEFAULT_WIDGET_ATTRIBUTES)
    )
    permissions = forms.ModelMultipleChoiceField(
        label=PERMISSIONS_LABEL,
        required=False,
        queryset=Permission.objects.all(),
        help_text=(
            'Specifying permissions individually is not necessary if the user belongs to a group '
            'to which those permissions are already allocated.'
        )
    )

    class Meta:
        model = User
        fields = [
            EMAIL_FIELD,
            # PASSWORD_FIELD,
            FIRST_NAME_FIELD,
            LAST_NAME_FIELD,
            AVATAR_FIELD,
            IS_SUPERUSER_FIELD,
            FORCE_PASSWORD_CHANGE_FIELD
        ]


class SocialAuthInline(TabularInline):
    """TODO: add docstring."""

    model = UserSocialAuth
    extra = 0
    readonly_fields: List[str] = []


class UserAdmin(BaseUserAdmin):
    """TODO: add docstring."""

    # The forms to add and change user instances
    form = UserChangeForm
    add_form = UserCreationForm

    # The fields to be used in displaying the User model.
    # These override the definitions on the base UserAdmin that reference specific fields on auth.User.
    list_display = [FIRST_NAME_FIELD, LAST_NAME_FIELD, USERNAME_FIELD, EMAIL_FIELD, 'last_login']

    list_filter = ['groups', IS_SUPERUSER_FIELD, 'is_active']

    fieldsets = (
        ('Basic Information', {
            CLASSES_KEY: ('wide',),
            FIELDS_KEY: (USERNAME_FIELD, EMAIL_FIELD, FIRST_NAME_FIELD, LAST_NAME_FIELD)
        }),
        ('Settings', {
            CLASSES_KEY: ('',),
            FIELDS_KEY: (FORCE_PASSWORD_CHANGE_FIELD, 'locked')
        }),
        (PERMISSIONS_LABEL, {
            FIELDS_KEY: (IS_SUPERUSER_FIELD, 'groups', 'permissions')
        }),
    )

    # add_fieldsets is not a standard ModelAdmin attribute.
    # UserAdmin overrides get_fieldsets to use this attribute when creating a user.
    add_fieldsets = (
        ('Basic Information (Required)', {
            CLASSES_KEY: ('wide',),
            FIELDS_KEY: (
                USERNAME_FIELD,
                EMAIL_FIELD,
                'password1',
                ('password2', FORCE_PASSWORD_CHANGE_FIELD)
            )
        }),
        ('Optional Information', {
            CLASSES_KEY: ('wide',),
            FIELDS_KEY: (FIRST_NAME_FIELD, LAST_NAME_FIELD)
        }),
        (PERMISSIONS_LABEL, {
            FIELDS_KEY: (IS_SUPERUSER_FIELD, 'groups', 'permissions')
        }),
    )

    search_fields = [FIRST_NAME_FIELD, LAST_NAME_FIELD, USERNAME_FIELD, EMAIL_FIELD]

    ordering = [LAST_NAME_FIELD, FIRST_NAME_FIELD]

    filter_horizontal = ()

    inlines = [SocialAuthInline]

    # actions = ['some_action']
    #
    # def some_action(self, request, queryset):
    #     #do something...
    # some_action.short_description = "blabla"


admin_site.register(User, UserAdmin)

admin_site.register(UserSocialAuth, UserSocialAuthOption)
admin_site.register(Nonce, NonceOption)
admin_site.register(Association, AssociationOption)
