# from forms.form import FormMixIn, CustomForm

from django.contrib.auth.forms import AuthenticationForm, UserCreationForm as BaseUserCreationForm
from account.models import User

from django.urls import reverse
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit, Layout, Field, HTML
from django.forms import ValidationError


class LoginForm(AuthenticationForm):
    """Crispy login form."""
    def __init__(self, request=None, *args, **kwargs):
        super().__init__(request=request, *args, **kwargs)
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
            Field('username', css_class='form-control mb-4', placeholder='Username or email address'),
            Field('password', css_class='form-control mb-4', placeholder='Password'),
            HTML(f'''
                <div class="d-flex justify-content-around">
                    <div>
                        <!-- Remember me -->
                        <div class="custom-control custom-checkbox">
                            <input type="checkbox" class="custom-control-input" id="defaultLoginFormRemember">
                            <label class="custom-control-label" for="defaultLoginFormRemember">Remember me</label>
                        </div>
                    </div>
                    <div>
                        <!-- Forgot password -->
                        <a href="{reverse('account:password_reset')}">Forgot password?</a>
                    </div>
                </div>
            '''),
            Submit('submit', 'Sign in', css_class='btn btn-info btn-block my-4'),
            HTML(f'<p>Not a member? <a href="{reverse("account:register")}">Register</a></p>'),
            HTML(f'''
                <!-- Social login -->
                <p>or sign in with:</p>
                <a href='{reverse("social:begin", args=["facebook"])}' class="mx-2 btn-social btn-facebook" 
                   role="button" onclick="_gaq.push(['_trackEvent', 'btn-social', 'click', 'btn-facebook']);">
                    <i class="fab fa-facebook-f"></i>
                </a>
                <a href='{reverse("social:begin", args=["google-oauth2"])}' class="mx-2 btn-social btn-google" 
                   role="button" onclick="_gaq.push(['_trackEvent', 'btn-social', 'click', 'btn-google']);">
                    <i class="fab fa-google"></i>
                </a>
                <a href='{reverse("social:begin", args=["twitter"])}' class="mx-2 btn-social btn-twitter" 
                   role="button" onclick="_gaq.push(['_trackEvent', 'btn-social', 'click', 'btn-twitter']);">
                    <i class="fab fa-twitter"></i>
                </a>
            ''')
        )


class UserCreationForm(BaseUserCreationForm):
    class Meta:
        model = User
        exclude = ()
        # fields = ('username', 'email')


class RegistrationForm(UserCreationForm):
    """Crispy registration form."""

    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'username', 'email')

    def __init__(self, *args, **kwargs):
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
            HTML(f'''
                <div class="form-row mb-4">
                    <div class="col">
                        <!-- First name -->
            '''),
            Field('first_name', placeholder='First name'),
            HTML(f'''
                    </div>
                    <div class="col">
                        <!-- Last name -->
            '''),
            Field('last_name', placeholder='Last name'),
            HTML(f'''
                    </div>
                </div>
            '''),
            Field('email', css_class='form-control mb-4', placeholder='Email address'),
            Field('username', css_class='form-control mb-4', placeholder='Username'),
            Field('password1', css_class='form-control mb-4', placeholder='Password'),
            Field('password2', css_class='form-control mb-4', placeholder='Confirm password'),
            Submit('submit', 'Create account', css_class='btn btn-info btn-block my-4'),
            HTML(f'<p>Already have an account? <a href="{reverse("account:login")}">Sign in</a></p>'),
            HTML(f'''
                <!-- Social login -->
                <p>or sign in with:</p>
                <a href='{reverse("social:begin", args=["facebook"])}' class="mx-2 btn-social btn-facebook" 
                   role="button" onclick="_gaq.push(['_trackEvent', 'btn-social', 'click', 'btn-facebook']);">
                    <i class="fab fa-facebook-f"></i>
                </a>
                <a href='{reverse("social:begin", args=["google-oauth2"])}' class="mx-2 btn-social btn-google" 
                   role="button" onclick="_gaq.push(['_trackEvent', 'btn-social', 'click', 'btn-google']);">
                    <i class="fab fa-google"></i>
                </a>
            ''')
        )

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if not self.cleaned_data.get('username'):
            self.cleaned_data['username'] = email
        if email and User.objects.filter(email=email).exists():
            raise ValidationError('An account with this email address has already been created.')
        return email

    def clean_username(self):
        email = self.cleaned_data.get('email')
        username = self.cleaned_data.get('username') if self.cleaned_data.get('username') else email
        if email:
            if User.objects.filter(email=email).count() > 0:
                raise ValidationError('An account with this email address has already been created.')
        if username:
            if User.objects.filter(username=username).count() > 0:
                raise ValidationError('An account with this username has already been created.')
        return username

    def clean_first_name(self):
        first_name = self.cleaned_data.get('first_name')
        first_name = first_name.title()
        return first_name

    def clean_last_name(self):
        last_name = self.cleaned_data.get('last_name')
        last_name = last_name.title()
        return last_name

    def clean(self):
        cleaned_data = super().clean()
        # if cleaned_data.get('username') is None:
        #     cleaned_data['username'] = cleaned_data.get('email')
        if cleaned_data.get('password1') != cleaned_data.get('password2'):
            raise ValidationError('Your passwords need to match. Please try again.')
        return cleaned_data


# class ChangeForm(FormMixIn, forms.ModelForm):
#     # Form for updating user information
#     form_id = 'changeform' # set in __init__ below
#     action = None # None means form submits to the current page
#     method = 'POST'
#     enctype = "multipart/form-data"
#     submit = 'Update'
#     classes = [ 'formlib-form form-horizontal' ] # list of default classes for the form: <form>
#     field_classes = [ '' ]
#
#     class Meta:
#         model = User
#         fields = [ 'first_name', 'last_name', 'email', 'username', 'address', 'address2', 'city', 'state', 'zip_code', 'date_of_birth', 'phone_number', ]
#         widgets = {
#             # 'name': forms.TextInput(attrs={'class': 'form-control'}),
#         }
#
#     def init(self):
#         self.fields['first_name'] = forms.CharField(required=True, max_length=100, initial=self.request.user.first_name, widget=forms.TextInput(attrs={'class': 'form-control'}))
#         self.fields['last_name'] = forms.CharField(required=True, max_length=100, initial=self.request.user.last_name, widget=forms.TextInput(attrs={'class': 'form-control'}))
#         self.fields['email'] = forms.EmailField(required=True, initial=self.request.user.email, widget=forms.TextInput(attrs={'class': 'form-control'}))
#         self.fields['username'] = forms.CharField(required=True, initial=self.request.user.username, max_length=100, widget=forms.TextInput(attrs={'class': 'form-control'}))
#         self.fields['address'] = forms.CharField(required=False, max_length=100, initial=self.request.user.address, widget=forms.TextInput(attrs={'class': 'form-control'}))
#         self.fields['address2'] = forms.CharField(label='Address (line 2)', initial=self.request.user.address2, required=False, max_length=100, widget=forms.TextInput(attrs={'class': 'form-control'}))
#         self.fields['city'] = forms.CharField(required=False, max_length=40, initial=self.request.user.city, widget=forms.TextInput(attrs={'class': 'form-control'}))
#         self.fields['state'] = forms.CharField(required=False, max_length=2, initial=self.request.user.state, widget=forms.TextInput(attrs={'class': 'form-control'}))
#         self.fields['zip_code'] = forms.CharField(required=False, max_length=5, initial=self.request.user.zip_code, widget=forms.TextInput(attrs={'class': 'form-control'}))
#         self.fields['date_of_birth'] = forms.DateField(label='Date of birth', required=False, initial=self.request.user.date_of_birth, widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}))
#         self.fields['phone_number'] = forms.CharField(required=False, max_length=20, initial=self.request.user.phone_number, widget=forms.TextInput(attrs={'class': 'form-control'}))
#         # self.fields['picture'] = forms.ImageField(label='Profile picture', rinitial=self.request.user.pict, equired=False)
#         p = self.request.user
#
#     def clean_picture(self):
#         picture = self.cleaned_data.get("picture", False)
#         if picture and picture.file:
#             picture.file.seek(0)
#             mime = magic.from_buffer(picture.file.getvalue(), mime=True)
#             print(">>> The mime type is %s." % mime)
#             if mime not in ("image/png", "image/jpeg", "image/jpg"):
#                 raise forms.ValidationError("The file type must be JPG or PNG.")
#         return picture
#
#     def clean_username(self):
#         username = self.cleaned_data.get('username')
#         if username != self.request.user.username: # the username has been changed
#             try:
#                 user = User.objects.get(username=self.cleaned_data.get('username'))
#                 raise forms.ValidationError('This username has been taken.')
#             except User.DoesNotExist:
#                 pass
#         return username
#
#     def clean_date_of_birth(self):
#         if self.cleaned_data.get('date_of_birth') is not None and self.cleaned_data.get('date_of_birth') > datetime.date.today():
#             raise forms.ValidationError('This date is in the future. Currently, we only support users who were born in the past... (: ')
#         return self.cleaned_data.get('date_of_birth')
#
#
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
