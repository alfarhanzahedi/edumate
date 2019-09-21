from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.forms import UserChangeForm
from django.db import transaction

from .models import User
from .models import Student
from .models import Teacher
from .constants import Role

class CustomUserCreationForm(UserCreationForm):
    ROLES = [(Role.STUDENT, 'Student'), (Role.TEACHER, 'Teacher')]
    role = forms.ChoiceField(widget = forms.RadioSelect, choices = ROLES)

    class Meta(UserCreationForm):
        model = User
        fields = ('username', 'email', 'role')
    
    def clean_email(self):
        email = self.cleaned_data.get('email')
        try:
            User.objects.get(email = email)
        except User.DoesNotExist:
            return email
        raise forms.ValidationError('This email address is already in use.')

class CustomUserChangeForm(UserChangeForm):

    class Meta(UserChangeForm):
        model = User
        fields = ('username', 'email')

    def clean_email(self):
        email = self.cleaned_data.get('email')
        try:
            User.objects.get(email = email)
        except User.DoesNotExist:
            return email
        raise forms.ValidationError('This email address is already in use.')