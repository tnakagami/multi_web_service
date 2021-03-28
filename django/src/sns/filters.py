from django import forms
from django.db.models import Q
from django.contrib.auth import get_user_model
from django.utils.translation import ugettext_lazy
import django_filters as filters

User = get_user_model()

class UserFilter(filters.FilterSet):
    name = filters.CharFilter(
        widget=forms.TextInput(attrs={
            'placeholder': ugettext_lazy('username or viewname'),
            'class': 'form-control',
        }),
        method='filter_userinfo',
    )

    class Meta:
        model = User
        fields = ['name',]

    def filter_userinfo(self, queryset, name, value):
        return queryset.filter(Q(username__icontains=value) | Q(viewname__icontains=value))

    def qs(self):
        queryset = super().qs

        return queryset.filter(is_staff=False, is_active=True)
