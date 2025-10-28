from django import forms
from .models import Snapily
from django.contrib.auth.forms import UserCreationForm
from .models import *

class UserForm(forms.ModelForm):
    class Meta:
        model = Snapily
        fields = ['text', 'photo']

# <----- form for custum user ----->

class AlbumEditForm(forms.ModelForm):
    class Meta:
        model = Album
        fields = ["name", "share_family"]   # only these two editable
        widgets = {
            "name": forms.TextInput(attrs={"class": "form-control", "placeholder": "Album name"}),
            "share_family": forms.CheckboxInput(attrs={"class": "form-check-input"})
        }
