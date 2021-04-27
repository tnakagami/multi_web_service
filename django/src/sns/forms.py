from django.contrib.auth import get_user_model
from django import forms
from django.utils.translation import ugettext_lazy
from . import models

User = get_user_model()

class CreateTweetForm(forms.ModelForm):
    """
    Form of updating user status
    """
    class Meta:
        model = models.Tweet
        fields = ('text', )
        widgets = {
            'text': forms.Textarea(attrs={
                'rows': 4, 'cols': 15, 'style':'resize:none;'
            })
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        for field in self.fields.values():
            field.widget.attrs['class'] = 'form-control'

class CreateRelationshipForm(forms.ModelForm):
    """
    Form of updating follower status
    """
    owner_id = forms.IntegerField()
    follower_id = forms.IntegerField()

    class Meta:
        model = models.Relationship
        exclude = ('owner', 'follower')

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('request_user') if 'request_user' in kwargs else None
        super().__init__(*args, **kwargs)
        self.fields['owner_id'].widget = forms.HiddenInput()
        self.fields['follower_id'].widget = forms.HiddenInput()

    def clean_owner_id(self):
        owner_id = self.cleaned_data.get('owner_id')

        if self.user is None or owner_id != self.user.pk:
            raise forms.ValidationError(ugettext_lazy('Error: This POST request must be submitted by login user.'))

        return owner_id

    def clean_follower_id(self):
        follower_id = self.cleaned_data.get('follower_id')

        if self.user is None or follower_id == self.user.pk:
            raise forms.ValidationError(ugettext_lazy('Error: Login users cannot be registered as followers.'))

        return follower_id

    def save(self, commit=True):
        owner_id = self.cleaned_data.get('owner_id')
        follower_id = self.cleaned_data.get('follower_id')

        owner = User.objects.get(pk=owner_id)
        follower = User.objects.get(pk=follower_id)
        instance, _ = models.Relationship.objects.get_or_create(owner=owner, follower=follower)

        if commit:
            instance.save()

        return instance
