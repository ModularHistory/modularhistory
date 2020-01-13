from django import forms
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import Group, Permission

from .models import User
from admin import admin_site

# from .forms import UserCreationForm #  UserChangeForm


class UserCreationForm(forms.ModelForm):
    """A form for creating new users. Includes all the required
    fields, plus a repeated password."""
    username = forms.CharField(required=False, widget=forms.HiddenInput())
    email = forms.EmailField(label='Email', required=True, max_length=100, widget=forms.TextInput(attrs={'class': 'form-control'}))
    first_name = forms.CharField(label='First Name', required=False, max_length=100, widget=forms.TextInput(attrs={'class': 'form-control'}))
    last_name = forms.CharField(label='Last Name', required=False, max_length=100, widget=forms.TextInput(attrs={'class': 'form-control'}))
    password1 = forms.CharField(label='Password', widget=forms.PasswordInput)
    password2 = forms.CharField(label='Password confirmation', widget=forms.PasswordInput)
    force_password_change = forms.BooleanField(help_text='Prompt user to change password upon first login', required=False, initial=True)
    groups = forms.ModelMultipleChoiceField(label="Groups", required=False, queryset=Group.objects.all(), widget=forms.CheckboxSelectMultiple(attrs={'class': 'form-control'}))
    permissions = forms.ModelMultipleChoiceField(label="Permissions", required=False, queryset=Permission.objects.all(), help_text='Specifying permissions individually is not necessary if the user belongs to a group to which those permissions are already allocated.')

    class Meta:
        model = User
        fields = (
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
        )

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).count() > 0:
            raise forms.ValidationError('An account with this email address has already been created.')
        return email

    def clean_username(self):
        username = self.cleaned_data.get('email') if not self.cleaned_data.get("username") else self.cleaned_data.get("username")
        if User.objects.filter(username=username).count() > 0:
            raise forms.ValidationError('An account with this username has already been created.')
        return username

    def clean_password2(self):
        # Check that the two password entries match
        password1 = self.cleaned_data.get("password1")
        password2 = self.cleaned_data.get("password2")
        if password1 and password2 and password1 != password2:
            raise forms.ValidationError("Passwords don't match.")
        return password2

    def save(self, commit=True):
        # Save the provided password in hashed format
        user = super(UserCreationForm, self).save(commit=False)
        user.username = self.cleaned_data.get("email") if not self.cleaned_data.get("username") else self.cleaned_data.get("username")
        user.set_password(self.cleaned_data["password1"])
        if commit:
            user.save()
        return user


class UserChangeForm(forms.ModelForm):
    """A form for updating users. Includes all the fields on
    the user, but replaces the password field with admin's
    password hash display field.
    """
    # password = ReadOnlyPasswordHashField()
    # gender = forms.ChoiceField(label='Gender', required=True, choices=settings.GENDERS, widget=forms.Select(attrs={}))
    username = forms.CharField(required=False, widget=forms.HiddenInput())
    email = forms.EmailField(label='Email', required=True, max_length=100,
                             widget=forms.TextInput(attrs={'class': 'form-control'}))
    first_name = forms.CharField(label='First Name', required=False, max_length=100,
                                 widget=forms.TextInput(attrs={'class': 'form-control'}))
    last_name = forms.CharField(label='Last Name', required=False, max_length=100,
                                widget=forms.TextInput(attrs={'class': 'form-control'}))
    force_password_change = forms.BooleanField(label='Force password change', required=False)
    locked = forms.BooleanField(label='Locked', required=False)
    # password1 = forms.CharField(label='Password', widget=forms.PasswordInput)
    # password2 = forms.CharField(label='Password confirmation', widget=forms.PasswordInput)
    # force_password_change = forms.BooleanField(help_text='Prompt user to change password upon first login', required=False, initial=True)
    groups = forms.ModelMultipleChoiceField(
        label="Groups", required=False, queryset=Group.objects.all(),
        widget=forms.CheckboxSelectMultiple(attrs={'class': 'form-control'})
    )
    permissions = forms.ModelMultipleChoiceField(
        label="Permissions", required=False, queryset=Permission.objects.all(),
        help_text=('Specifying permissions individually is not necessary if the user belongs to a group '
                   'to which those permissions are already allocated.')
    )

    class Meta:
        model = User
        fields = (
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
        )


class UserAdmin(BaseUserAdmin):
    # The forms to add and change user instances
    form = UserChangeForm
    add_form = UserCreationForm

    # The fields to be used in displaying the User model.
    # These override the definitions on the base UserAdmin that reference specific fields on auth.User.
    list_display = ('first_name', 'last_name', 'email', 'username', 'last_login')

    list_filter = ('groups', 'is_superuser', 'is_active',)

    fieldsets = (
        ('Basic Information', {
            'classes': ('wide',),
            # 'fields': ('username', 'email', 'password1', ('password2','force_password_change',), )
            'fields': ('username', 'email', )
        }),
        ('Additional Information', {
            'classes': ('wide',),
            'fields': ('first_name', 'last_name')
        }),
        ('Functional Information', {
            'classes': ('',),
            'fields': ('force_password_change', 'locked',)
        }),
        ('Permissions', {
            'fields': ('is_superuser', 'groups', 'permissions',)
        }),
    )

    # add_fieldsets is not a standard ModelAdmin attribute.
    # UserAdmin overrides get_fieldsets to use this attribute when creating a user.
    add_fieldsets = (
        ('Basic Information (Required)', {
            'classes': ('wide',),
            'fields': ('username', 'email', 'password1', ('password2', 'force_password_change',), )
        }),
        ('Optional Information', {
            'classes': ('wide',),
            'fields': ('first_name', 'last_name')
        }),
        ('Permissions', {
            'fields': ('is_superuser', 'groups', 'permissions',)
        }),
    )

    search_fields = ('first_name', 'last_name', 'email', 'username')

    ordering = ('last_name', 'first_name')

    filter_horizontal = ()

    # actions = ['some_action']
    #
    # def some_action(self, request, queryset):
    #     #do something...
    # some_action.short_description = "blabla"


admin_site.register(User, UserAdmin)
