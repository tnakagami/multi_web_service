import web_service.widgets as widgets
from django.core.files.storage import default_storage
from django import forms
from django.db.models import Q
from django.utils.translation import ugettext_lazy
from django.db import transaction
from . import models

class PostSearchForm(forms.Form):
    """
    post searching form
    """
    search_word = forms.CharField(
        label=ugettext_lazy('keyword'),
        required=False,
        widget=forms.TextInput(
            attrs={'placeholder': ugettext_lazy('keyword (target: title, text, keywords)'), 'class': 'form-control'}
        ),
    )
    tags = forms.ModelMultipleChoiceField(
        label=ugettext_lazy('filtered by tag'),
        required=False,
        queryset=models.Tag.objects.order_by('name'),
        widget=widgets.CustomCheckboxSelectMultiple,
    )

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)

        if user is not None:
            self.fields['tags'].queryset = models.Tag.objects.filter(user=user).order_by('name')

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
                queryset = queryset.filter(Q(title__icontains=word) | Q(text__icontains=word) | Q(keywords__icontains=word))

        return queryset

class TagSearchForm(forms.Form):
    """
    tag searching form
    """
    search_word = forms.CharField(
        label=ugettext_lazy('keyword'),
        required=False,
        widget=forms.TextInput(
            attrs={'placeholder': ugettext_lazy('keyword'), 'class': 'form-control'}
        ),
    )

    def filtered_queryset(self, queryset):
        # get tags
        search_word = self.cleaned_data.get('search_word')

        if search_word:
            for word in search_word.split():
                queryset = queryset.filter(name__icontains=word)

        return queryset

class TagForm(forms.ModelForm):
    class Meta:
        model = models.Tag
        fields = ('name',)

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)

        if user is not None:
            self.fields['name'].queryset = models.Tag.objects.filter(user=user).order_by('name')
        for field in self.fields.values():
            field.widget.attrs['class'] = 'form-control'

class PostForm(forms.ModelForm):
    class Meta:
        model = models.Post
        fields = ('title', 'text', 'tags', 'relation_posts', 'is_public', 'description', 'keywords')
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'form-control'
            }),
            'text': widgets.UploadableTextarea(attrs={
                'placeholder': ugettext_lazy('Markdown support\n\n## Introduction\nThis is sample text.'),
                'rows': 20, 'cols': 10, 'style': 'resize:none;',
                'class': 'form-control',
            }),
            'tags': forms.SelectMultiple(attrs={
                'class': 'dual-listbox',
            }),
            'relation_posts': forms.SelectMultiple(attrs={
                'class': 'dual-listbox',
            }),
            'is_public': forms.CheckboxInput(attrs={
                'data-toggle': 'toggle',
                'data-onstyle': 'primary',
                'data-offstyle': 'danger',
                'data-on': 'Public',
                'data-off': 'Private',
            }),
            'description': forms.Textarea(attrs={
                'rows': 5, 'cols': 10, 'style':'resize:none;', 'class': 'form-control',
            }),
            'keywords': forms.TextInput(attrs={
                'placeholder': ugettext_lazy('keyword'), 'class': 'form-control',
            }),
        }

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        post_pk = kwargs.pop('pk', None)
        super().__init__(*args, **kwargs)

        if user is not None:
            tag_queryset = models.Tag.objects.filter(user=user).order_by('name')
            post_queryset = models.Post.objects.filter(is_public=True, user=user).order_by('title')
            self.fields['tags'].queryset = tag_queryset
            # self post is ignored
            self.fields['relation_posts'].queryset = post_queryset if post_pk is None else post_queryset.exclude(pk=post_pk)

class CommentForm(forms.ModelForm):
    class Meta:
        model = models.Comment
        fields = ('name', 'text')
        widgets = {
            'text': forms.Textarea(attrs={
                'placeholder': ugettext_lazy('Markdown support\n\n## Comment\nThis is comment.\n\n[link text](http://link/to/page)\n\n![image alt](path/to/image)'),
                'rows': 5, 'cols': 10, 'style':'resize:none;',
            })
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        for field in self.fields.values():
            field.widget.attrs['class'] = 'form-control'

class ReplyForm(forms.ModelForm):
    class Meta:
        model = models.Reply
        fields = ('name', 'text')
        widgets = {
            'text': forms.Textarea(attrs={
                'placeholder': ugettext_lazy('Markdown support\n\n## Reply\nThis is reply.\n\n[link text](http://link/to/page)\n\n![image alt](path/to/image)'),
                'rows': 5, 'cols': 10, 'style':'resize:none;',
            })
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
