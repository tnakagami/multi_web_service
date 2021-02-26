import web_service.widgets as widgets
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
