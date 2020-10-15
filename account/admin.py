from typing import List

from django import forms
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import Group, Permission
from social_django.models import UserSocialAuth

from account.models import User
# from account.forms import UserCreationForm #  UserChangeForm
from admin import TabularInline, admin_site

MAX_EMAIL_LENGTH: int = 100
MAX_NAME_LENGTH: int = 100


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
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    first_name = forms.CharField(
        label='First Name',
        required=False,
        max_length=MAX_NAME_LENGTH,
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    last_name = forms.CharField(
        label='Last Name',
        required=False,
        max_length=MAX_NAME_LENGTH,
        widget=forms.TextInput(attrs={'class': 'form-control'})
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
        widget=forms.CheckboxSelectMultiple(attrs={'class': 'form-control'})
    )
    permissions = forms.ModelMultipleChoiceField(
        label='Permissions',
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
            'email',
            'password',
            'first_name',
            'last_name',
            # 'address',
            # 'address2',
            # 'city',
            # 'state',
            # 'zip_code',
            # 'date_of_birth',
            # 'phone_number',
            # 'gender',
            'avatar',
            'is_superuser',
            'force_password_change'
        ]

    def clean_email(self):
        """TODO: add docstring."""
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).count() > 0:
            raise forms.ValidationError('An account with this email address has already been created.')
        return email

    def clean_username(self):
        """TODO: add docstring."""
        username = self.cleaned_data.get('username') or self.cleaned_data.get('email')
        if User.objects.filter(username=username).count() > 0:
            raise forms.ValidationError('An account with this username has already been created.')
        return username

    def clean_password2(self):
        """TODO: add docstring."""
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
        user.username = self.cleaned_data.get('username') or self.cleaned_data.get('email')
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
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    last_name = forms.CharField(
        label='Last Name',
        required=False,
        max_length=MAX_NAME_LENGTH,
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    force_password_change = forms.BooleanField(label='Force password change', required=False)
    locked = forms.BooleanField(label='Locked', required=False)
    groups = forms.ModelMultipleChoiceField(
        label='Groups',
        required=False,
        queryset=Group.objects.all(),
        widget=forms.CheckboxSelectMultiple(attrs={'class': 'form-control'})
    )
    permissions = forms.ModelMultipleChoiceField(
        label='Permissions',
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
            'email',
            # 'password',
            'first_name',
            'last_name',
            # 'address',
            # 'address2',
            # 'city',
            # 'state',
            # 'zip_code',
            # 'date_of_birth',
            'avatar',
            'is_superuser',
            'force_password_change'
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
    list_display = ['first_name', 'last_name', 'email', 'username', 'last_login']

    list_filter = ['groups', 'is_superuser', 'is_active']

    fieldsets = (
        ('Basic Information', {
            'classes': ('wide',),
            # 'fields': ('username', 'email', 'password1', ('password2','force_password_change',), )
            'fields': ('username', 'email', 'first_name', 'last_name')
        }),
        ('Settings', {
            'classes': ('',),
            'fields': ('force_password_change', 'locked')
        }),
        ('Permissions', {
            'fields': ('is_superuser', 'groups', 'permissions')
        }),
    )

    # add_fieldsets is not a standard ModelAdmin attribute.
    # UserAdmin overrides get_fieldsets to use this attribute when creating a user.
    add_fieldsets = (
        ('Basic Information (Required)', {
            'classes': ('wide',),
            'fields': ('username', 'email', 'password1', ('password2', 'force_password_change'))
        }),
        ('Optional Information', {
            'classes': ('wide',),
            'fields': ('first_name', 'last_name')
        }),
        ('Permissions', {
            'fields': ('is_superuser', 'groups', 'permissions')
        }),
    )

    search_fields = ['first_name', 'last_name', 'email', 'username']

    ordering = ['last_name', 'first_name']

    filter_horizontal = ()

    inlines = [SocialAuthInline]

    # actions = ['some_action']
    #
    # def some_action(self, request, queryset):
    #     #do something...
    # some_action.short_description = "blabla"


admin_site.register(User, UserAdmin)
