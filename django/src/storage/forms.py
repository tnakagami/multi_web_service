from django import forms
from django.template.defaultfilters import filesizeformat
from django.utils.translation import ugettext_lazy
from . import models
import os

class UploadFileForm(forms.ModelForm):
    file = forms.FileField(
        label=ugettext_lazy('upload file'),
        widget=forms.FileInput(attrs={'class': 'custom-file-input'}),
    )

    class Meta:
        model = models.FileStorage
        fields = ('file', )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # max upload size: 30MB
        self.MAX_UPLOAD_SIZE = 30 * 1024 * 1024

    def clean(self):
        cleaned_data = super().clean()
        file = cleaned_data.get('file')

        try:
            # check file size
            if file.size > self.MAX_UPLOAD_SIZE:
                max_size = filesizeformat(str(self.MAX_UPLOAD_SIZE))
                current_size = filesizeformat(file.size)
                raise forms.ValidationError(ugettext_lazy('Please keep filesize under {}. Current filesize {}'.format(max_size, current_size)))
        except AttributeError:
            pass

        return cleaned_data

    def save(self, commit=True):
        # get forms.FileField instance
        file = self.cleaned_data.get('file')
        # create model instance
        instance = super().save(commit=False)
        # update filename in model instance
        instance.filename = os.path.basename(file.name)

        if commit:
            instance.save()

        return instance

class FileSearchForm(forms.Form):
    """
    file searching form
    """
    search_word = forms.CharField(
        label=ugettext_lazy('filename'),
        required=True,
        widget=forms.TextInput(
            attrs={'placeholder': ugettext_lazy('filename'), 'class': 'form-control'}
        ),
    )

    def filtered_queryset(self, queryset):
        # get search word
        search_word = self.cleaned_data.get('search_word')

        if search_word:
            for word in search_word.split():
                queryset = queryset.filter(filename__icontains=word)

        return queryset
