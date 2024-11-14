from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm,AuthenticationForm
from django.forms import CharField,TextInput,EmailField, EmailInput,PasswordInput
from django import forms

class RegisterForm(UserCreationForm):
    username = forms.CharField(max_length=100,
                               required=True,
                               widget=forms.TextInput())

    email = forms.CharField(max_length=100,
                               required=True,
                               widget=forms.TextInput())

    password1 = forms.CharField(max_length=50,
                                required=True,
                                widget=forms.PasswordInput())

    password2 = forms.CharField(max_length=50,
                                required=True,
                                widget=forms.PasswordInput())
    class Meta:
        model = User
        fields = ('username','email','password1','password2')

class LoginForm(AuthenticationForm):
    username = CharField(max_length=16, min_length=3, required=True,widget=TextInput(attrs={'class': 'form-control'}))
    password = CharField(max_length=16, min_length=3, required=True,widget=PasswordInput(attrs={'class': 'form-control'}))

    class Meta:
        model = User
        fields = ('username', 'password')

