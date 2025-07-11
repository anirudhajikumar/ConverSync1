from django import forms
from django.views import generic
from django.forms import ModelForm
from .models import Room, Profile
from django.contrib.auth.models import User
from django.urls import reverse_lazy
from django.contrib.auth.forms import UserCreationForm




class RoomForm(ModelForm):
    class Meta:
        model = Room
        fields = ['topic', 'name', 'description']
        widgets = {
            'topic': forms.Select(attrs={'class': 'form-control'}),
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control'})
        }
        
        
class editProfilePage(ModelForm):
    class Meta:
        model = Profile
        fields = ['name', 'bio', 'profile_pic']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'bio': forms.Textarea(attrs={'class': 'form-control'})
        }
        


class signUpForm(UserCreationForm):
    class Meta:
        model = User
        fields = ['username', 'password1', 'password2']

    def __init__(self, *args, **kwargs):
        super(signUpForm, self).__init__(*args, **kwargs)
        for field_name in self.fields:
            self.fields[field_name].widget.attrs.update({
                'class': 'form-control'
            })
