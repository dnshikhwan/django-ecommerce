
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django import forms

# for login
from django.contrib.auth.forms import AuthenticationForm
from django.forms.widgets import PasswordInput, TextInput

# Registration form


class CreateUserForm(UserCreationForm):

    class Meta:
        model = User

        # field for data that we need from user to register
        # password2 is password confirmation that need to match password1
        fields = ['username', 'email', 'password1', 'password2']

    # to access data in the fields
    def __init__(self, *args, **kwargs):
        super(CreateUserForm, self).__init__(*args, **kwargs)

        self.fields['email'].required = True

    # to validate email
    def clean_email(self):
        email = self.cleaned_data.get('email')

        if User.objects.filter(email=email).exists():
            raise forms.ValidationError('This email is invalid')

        # Len function updated
        if len(email) >= 350:
            raise forms.ValidationError('Your email is too long')

        return email

# Login form


class LoginForm(AuthenticationForm):
    username = forms.CharField(widget=TextInput())
    password = forms.CharField(widget=PasswordInput())

# form to update username and email


class UpdateUserForm(forms.ModelForm):
    password = None

    class Meta:
        model = User

        fields = ['username', 'email']
        exclude = ['password1', 'password2']

    # to access data in the fields and make the email required
    def __init__(self, *args, **kwargs):
        super(UpdateUserForm, self).__init__(*args, **kwargs)

        self.fields['email'].required = True

    # to validate email
    def clean_email(self):
        email = self.cleaned_data.get('email')

        # exclude checking for the email of the current authenticated user
        if User.objects.filter(email=email).exclude(pk=self.instance.pk).exists():
            raise forms.ValidationError('This email is invalid')

        # Len function updated
        if len(email) >= 350:
            raise forms.ValidationError('Your email is too long')

        return email
