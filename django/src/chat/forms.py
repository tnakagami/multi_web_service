from django import forms
from django.utils.translation import ugettext_lazy
from django.contrib.auth import get_user_model
from . import models

User = get_user_model()

class RoomSearchForm(forms.Form):
    """
    room searching form
    """
    search_word = forms.CharField(
        label=ugettext_lazy('keyword'),
        required=False,
        widget=forms.TextInput(
            attrs={'placeholder': ugettext_lazy('room name'), 'class': 'form-control'}
        ),
    )

    def filtered_queryset(self, queryset):
        # get search word
        search_word = self.cleaned_data.get('search_word')

        if search_word:
            for word in search_word.split():
                queryset = queryset.filter(name__icontains=word)

        return queryset

class RoomForm(forms.ModelForm):
    class Meta:
        model = models.Room
        fields = ('name', 'description', 'assigned')
        widgets = {
            'name': forms.TextInput(attrs={'placeholder': ugettext_lazy('room name'), 'class': 'form-control'}),
            'description': forms.Textarea(attrs={'rows': 5, 'cols': 10, 'style':'resize:none;', 'class': 'form-control',}),
            'assigned': forms.CheckboxSelectMultiple(attrs={
                'data-toggle': 'toggle',
                'data-onstyle': 'primary',
                'data-offstyle': 'secondary',
            }),
        }

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)

        if user is not None:
            self.fields['assigned'].queryset = User.objects.filter(is_superuser=False, is_staff=False).exclude(pk=user.pk)
