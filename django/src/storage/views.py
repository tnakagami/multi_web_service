from django.contrib.auth import get_user_model
from django.contrib.auth.mixins import LoginRequiredMixin, AccessMixin
from django.shortcuts import redirect
from django.urls import reverse_lazy, reverse
from django.views.generic import ListView, CreateView, DeleteView
from django.http import Http404
from . import models, forms

User = get_user_model()

class StorageListView(LoginRequiredMixin, ListView):
    """
    storage file list
    """
    model = models.FileStorage
    template_name = 'storage/index.html'
    paginate_by = 30
    context_object_name = 'files'

    def get_queryset(self):
        queryset = super().get_queryset().filter(user=self.request.user)
        form = forms.FileSearchForm(self.request.GET or None)

        # check form
        if form.is_valid():
            queryset = form.filtered_queryset(queryset)
        # ordering
        queryset = queryset.order_by('-created_at')

        return queryset

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        context['search_form'] = forms.FileSearchForm(self.request.GET or None)
        context['upload_form'] = forms.UploadFileForm(self.request.GET or None)

        return context

class FileUploadView(LoginRequiredMixin, CreateView):
    model = models.FileStorage
    template_name = 'storage/index.html'
    form_class = forms.UploadFileForm
    success_url = reverse_lazy('storage:index')

    def get(self, request, *args, **kwargs):
        return self.handle_no_permission()

    def form_valid(self, form):
        instance = form.save(commit=False)
        instance.user = self.request.user
        instance.save()

        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['search_form'] = forms.FileSearchForm(self.request.GET or None)

        if 'form' in context:
            context['upload_form'] = context['form']
            del context['form']
        else
            context['upload_form'] = forms.UploadFileForm(self.request.GET or None)

        return context

class FileDeleteView(AccessMixin, DeleteView):
    raise_exception = True
    model = models.FileStorage
    success_url = reverse_lazy('storage:index')

    def dispatch(self, request, *args, **kwargs):
        try:
            instance = self.model.objects.get(pk=kwargs['pk'])
        except Exception:
            return Http404

        # if user is not authenticated or instance is not request user's
        if not request.user.is_authenticated or request.user.pk != instance.user.pk:
            return self.handle_no_permission()
        # checks pass let http method handlers process the request
        return super().dispatch(request, *args, **kwargs)
