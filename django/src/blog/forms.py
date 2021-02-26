import web_service.widgets as widgets
from django.core.files.storage import default_storage
from django import forms
from django.db.models import Q
from . import models

class PostSearchForm(forms.Form):
    """
    post searching form
    """
    search_word = forms.CharField(
        label='keyword',
        required=True,
        widget=forms.TextInput(
            attrs={'placeholder': 'keyword', 'class': 'form-control'}
        ),
    )
    tags = forms.ModelMultipleChoiceField(
        label='filtered by tag',
        required=False,
        queryset=models.Tag.objects.order_by('name'),
        widget=widgets.CustomCheckboxSelectMultiple,
    )

    def filtered_queryset(self, queryset):
        # get tags
        tags = self.cleaned_data.get('tags')
        # get search word
        search_word = self.cleaned_data.get('search_word')

        if tags:
            for tag in tags:
                queryset = queryset.filter(tags=tag)
        if search_word:
            for word in search_word.split():
                queryset = queryset.filter(Q(title__icontains=word) | Q(text__icontains=word))

        return queryset

class TagForm(forms.ModelForm):
    class Meta:
        model = models.Tag
        exclude = ('user',)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        for field in self.fields.values():
            field.widget.attrs['class'] = 'form-control'

class PostForm(forms.ModelForm):
    class Meta:
        model = models.Post
        fields = ('title', 'text', 'tags', 'relation_posts', 'is_public', 'description', 'keywords')
        widgets = {
            'text': widgets.UploadableTextarea(attrs={'placeholder': '[TOC]\n\n## Introduction\n This is sample text.'}),
            'is_public': forms.CheckboxInput(attrs={
                'data-toggle': 'toggle',
                'data-onstyle': 'primary',
                'data-offstyle': 'danger',
                'data-on': 'Public',
                'data-off': 'Private',
            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        for field in self.fields.values():
            field.widget.attrs['class'] = 'form-control'

class FileUploadForm(forms.Form):
    upload_file = forms.FileField()

    def save(self):
        upload_file = self.cleaned_data['upload_file']
        file_name = default_storage.save(upload_file.name, upload_file)
        file_url = default_storage.url(file_name)

        return file_url
