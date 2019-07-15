from django import forms
from django.utils.translation import ugettext_lazy as _
from django.contrib.auth.forms import UserCreationForm


from user.models import User


class UserForm(UserCreationForm):

    class Meta:
        model = User
        fields = ['email']





