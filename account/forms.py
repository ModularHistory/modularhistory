from crispy_forms.helper import FormHelper
from crispy_forms.layout import Field, HTML, Layout, Submit

# from forms.form import FormMixIn, CustomForm
from django.contrib.auth.forms import (
    AuthenticationForm,
    UserCreationForm as BaseUserCreationForm,
)
from django.forms import ValidationError
from django.urls import reverse

from account.models import User
from account.admin import EMAIL_FIELD, USERNAME_FIELD, PASSWORD_FIELD
from modularhistory.constants import SOCIAL_AUTH_URL_NAME

DEFAULT_FIELD_CLASSES = 'form-control mb-4'


class LoginForm(AuthenticationForm):
    """Crispy login form."""

    def __init__(self, request=None, *args, **kwargs):
        """Construct the login form."""
        super().__init__(request, *args, **kwargs)
        # https://django-crispy-forms.readthedocs.io/en/latest/form_helper.html
        self.helper = FormHelper()
        self.helper.form_id = 'loginForm'
        self.helper.form_class = 'text-center border border-light p-5'
        self.helper.form_method = 'post'
        self.helper.form_action = '/account/login'
        self.helper.label_class = 'hidden'
        # self.helper.field_class = 'col-lg-8'
        self.helper.layout = Layout(
            HTML('<p class="h4 mb-4">Sign in</p>'),
            Field(
                USERNAME_FIELD,
                css_class=DEFAULT_FIELD_CLASSES,
                placeholder='Username or email address',
            ),
            Field(
                PASSWORD_FIELD, css_class=DEFAULT_FIELD_CLASSES, placeholder='Password'
            ),
            HTML(
                f'''
                <div class="d-flex justify-content-around">
                    <div>
                        <!-- Remember me -->
                        <div class="custom-control custom-checkbox">
                            <input type="checkbox" id="defaultLoginFormRemember">
                            <label for="defaultLoginFormRemember">Remember me</label>
                        </div>
                    </div>
                    <div>
                        <!-- Forgot password -->
                        <a href="{reverse('account:password_reset')}">Forgot password?</a>
                    </div>
                </div>
                '''
            ),
            Submit('submit', 'Sign in', css_class='btn btn-info btn-block my-4'),
            HTML(
                f'<p>Not a member? <a href="{reverse("account:register")}">Register</a></p>'
            ),
            # self.SOCIAL_LOGIN_COMPONENT,
            HTML(
                f'''
                <!-- Social login -->
                <p>or sign in with:</p>
                <a href='{reverse(SOCIAL_AUTH_URL_NAME, args=["facebook"])}'
                   class="mx-2 btn-social btn-facebook" role="button"
                   onclick="_gaq.push(['_trackEvent', 'btn-social', 'click', 'btn-facebook']);">
                    <i class="fab fa-facebook-f"></i>
                </a>
                <a href='{reverse(SOCIAL_AUTH_URL_NAME, args=["twitter"])}'
                   class="mx-2 btn-social btn-twitter" role="button"
                   onclick="_gaq.push(['_trackEvent', 'btn-social', 'click', 'btn-twitter']);">
                    <i class="fab fa-twitter"></i>
                </a>
                <a href='{reverse(SOCIAL_AUTH_URL_NAME, args=["github"])}'
                   class="mx-2 btn-social btn-github" role="button"
                   onclick="_gaq.push(['_trackEvent', 'btn-social', 'click', 'btn-github']);">
                    <i class="fab fa-github"></i>
                </a>
                <!--
                <a href='{reverse(SOCIAL_AUTH_URL_NAME, args=["google-oauth2"])}'
                   class="mx-2 btn-social btn-google" role="button"
                   onclick="_gaq.push(['_trackEvent', 'btn-social', 'click', 'btn-google']);">
                    <i class="fab fa-google"></i>
                </a>
                -->
                '''
            ),
        )


class UserCreationForm(BaseUserCreationForm):
    """Admin form for user creation."""

    class Meta:
        model = User
        exclude = ()
        # fields = [USERNAME_FIELD, EMAIL_FIELD]


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
        self.helper.form_id = 'registrationForm'
        self.helper.form_class = 'text-center border border-light p-5'
        self.helper.form_method = 'post'
        self.helper.form_action = '/account/register'
        self.helper.label_class = 'hidden'
        # self.helper.field_class = 'col-lg-8'
        self.helper.layout = Layout(
            HTML('<p class="h4 mb-4">Register account</p>'),
            HTML(
                '<div class="form-row mb-4">' '<div class="col">' '<!-- First name -->'
            ),
            Field('first_name', placeholder='First name'),
            HTML('</div>' '<div class="col">' '<!-- Last name -->'),
            Field('last_name', placeholder='Last name'),
            HTML('</div>' '</div>'),
            Field(
                EMAIL_FIELD,
                css_class=DEFAULT_FIELD_CLASSES,
                placeholder='Email address',
            ),
            Field(
                USERNAME_FIELD, css_class=DEFAULT_FIELD_CLASSES, placeholder='Username'
            ),
            Field('password1', css_class=DEFAULT_FIELD_CLASSES, placeholder='Password'),
            Field(
                'password2',
                css_class=DEFAULT_FIELD_CLASSES,
                placeholder='Confirm password',
            ),
            Submit('submit', 'Create account', css_class='btn btn-info btn-block my-4'),
            HTML(
                f'<p>Already have an account? <a href="{reverse("account:login")}">Sign in</a></p>'
            ),
            # LoginForm.SOCIAL_LOGIN_COMPONENT,
            HTML(
                f'''
                <!-- Social login -->
                <p>or sign in with:</p>
                <a href='{reverse(SOCIAL_AUTH_URL_NAME, args=["facebook"])}'
                   class="mx-2 btn-social btn-facebook" role="button"
                   onclick="_gaq.push(['_trackEvent', 'btn-social', 'click', 'btn-facebook']);">
                    <i class="fab fa-facebook-f"></i>
                </a>
                <a href='{reverse(SOCIAL_AUTH_URL_NAME, args=["twitter"])}'
                   class="mx-2 btn-social btn-twitter" role="button"
                   onclick="_gaq.push(['_trackEvent', 'btn-social', 'click', 'btn-twitter']);">
                    <i class="fab fa-twitter"></i>
                </a>
                <a href='{reverse(SOCIAL_AUTH_URL_NAME, args=["github"])}'
                   class="mx-2 btn-social btn-github" role="button"
                   onclick="_gaq.push(['_trackEvent', 'btn-social', 'click', 'btn-github']);">
                    <i class="fab fa-github"></i>
                </a>
                <!--
                <a href='{reverse(SOCIAL_AUTH_URL_NAME, args=["google-oauth2"])}'
                   class="mx-2 btn-social btn-google" role="button"
                   onclick="_gaq.push(['_trackEvent', 'btn-social', 'click', 'btn-google']);">
                    <i class="fab fa-google"></i>
                </a>
                -->
                '''
            ),
        )

    def clean_email(self):
        """Clean the email field value."""
        email = self.cleaned_data.get(EMAIL_FIELD)
        if not self.cleaned_data.get(USERNAME_FIELD):
            self.cleaned_data[USERNAME_FIELD] = email
        if email and User.objects.filter(email=email).exists():
            raise ValidationError(
                'An account with this email address has already been created.'
            )
        return email

    def clean_username(self):
        """Prepare the username field value to be saved."""
        email = self.cleaned_data.get(EMAIL_FIELD)
        username = self.cleaned_data.get(USERNAME_FIELD) or email
        if email:
            if User.objects.filter(email=email).count() > 0:
                raise ValidationError(
                    'An account with this email address already exists.'
                )
        if username:
            if User.objects.filter(username=username).count() > 0:
                raise ValidationError(
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
            raise ValidationError('Your passwords need to match. Please try again.')
        return cleaned_data


# class PictureForm(FormMixIn, forms.Form):
#     form_id = 'pictureform'
#     action = '/account/profile.picture/'
#     method = 'POST'
#     submit = 'Upload'
#     classes = [ 'formlib-form form-horizontal' ]
#     field_classes = [ '' ]
#     is_ajax = True
#
#     picture = forms.ImageField(label='Profile picture', required=False)
#
#     def clean_picture(self):
#         picture = self.cleaned_data.get("picture", False)
#         picture.file.seek(0)
#         mime = magic.from_buffer(picture.file.getvalue(), mime=True)
#         print(">>> The mime type is %s." % mime)
#         if mime not in ("image/png", "image/jpeg", "image/jpg"):
#             raise forms.ValidationError("The file type must be JPG or PNG.")
#         return picture
#
