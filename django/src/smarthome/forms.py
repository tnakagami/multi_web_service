from django import forms
from django.utils.translation import ugettext_lazy
from . import models

class AccessTokenForm(forms.ModelForm):
    class Meta:
        model = models.AccessToken
        fields = ('access_token', )
        widgets = {
            'token': forms.TextInput(attrs={
                'placeholder': ugettext_lazy('access token'), 'class': 'form-control',
            }),
        }
