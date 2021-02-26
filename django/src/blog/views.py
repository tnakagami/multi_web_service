from django.contrib.auth import get_user_model
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from . import models, forms

User = get_user_model()

class BlogListView(LoginRequiredMixin, ListView):
    """
    public blog list
    """
    model = models.Post
    template_name = 'blog/blog_list.html'
    paginate_by = 10
    context_object_name = 'blogs'

    def get_queryset(self):
        queryset = super().get_queryset()
        form = forms.PostSearchForm(self.request.GET or None)

        # check form
        if form.is_valid():
            queryset = form.filtered_queryset(queryset)
        # ordering
        queryset = queryset.order_by('-updated_at').prefetch_related('tags')

        return queryset

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        context['search_form'] = forms.PostSearchForm(self.request.GET or None)

        return context
