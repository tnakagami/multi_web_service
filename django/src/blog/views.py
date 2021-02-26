from django.contrib.auth import get_user_model
from django.contrib.auth.mixins import LoginRequiredMixin, AccessMixin
from django.urls import reverse_lazy, reverse
from django.http import Http404, JsonResponse, HttpResponseBadRequest
from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from . import models, forms

User = get_user_model()

class PostListView(LoginRequiredMixin, ListView):
    """
    public blog list
    """
    model = models.Post
    template_name = 'blog/index.html'
    paginate_by = 10
    context_object_name = 'posts'

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


class TagCreateView(LoginRequiredMixin, CreateView):
    raise_exception = True
    model = models.Tag
    form_class = forms.TagForm
    template_name = 'blog/tag_form.html'
    success_url = reverse_lazy('blog:index')

    def form_valid(self, form):
        instance = form.save(commit=False)
        instance.user = self.request.user
        instance.save()

        return super().form_valid(form)

class TagUpdateView(AccessMixin, UpdateView):
    raise_exception = True
    model = models.Tag
    form_class = forms.TagForm
    template_name = 'blog/tag_form.html'
    success_url = reverse_lazy('blog:index')

    def dispatch(self, request, *args, **kwargs):
        obj = self.model.objects.get(pk=kwargs['pk'])

        # if user is not authenticated
        if not request.user.is_authenticated:
            return self.handle_no_permission()
        # if obj is not request user's
        if request.user.pk != obj.user.pk:
            return redirect('blog:index')
        # checks pass let http method handlers process the request
        return super().dispatch(request, *args, **kwargs)

class PostCreateView(LoginRequiredMixin, CreateView):
    raise_exception = True
    model = models.Post
    form_class = forms.PostForm
    template_name = 'blog/post_form.html'
    success_url = reverse_lazy('blog:index')

    def form_valid(self, form):
        instance = form.save(commit=False)
        instance.user = self.request.user
        instance.save()

        return super().form_valid(form)

class PostUpdateView(AccessMixin, UpdateView):
    raise_exception = True
    model = models.Post
    form_class = forms.PostForm
    template_name = 'blog/post_form.html'

    def dispatch(self, request, *args, **kwargs):
        obj = self.model.objects.get(pk=kwargs['pk'])

        # if user is not authenticated
        if not request.user.is_authenticated:
            return self.handle_no_permission()
        # if obj is not request user's
        if request.user.pk != obj.user.pk:
            return redirect('blog:index')
        # checks pass let http method handlers process the request
        return super().dispatch(request, *args, **kwargs)

    def get_success_url(self):
        return reverse('blog:post_detail', kwargs={'pk': self.kwargs['pk']})

class PostDetailView(LoginRequiredMixin, DeleteView):
    model = models.Post

    def get_queryset(self):
        return super().get_queryset().prefetch_related('tags', 'comment_set__reply_set')

    def get_object(self, queryset=None):
        post = super().get_object()

        ret = post if post.is_public else Http404

        return ret

def image_upload(request):
    """
    upload image data
    """
    form = forms.FileUploadForm(files=request.FILES)

    if form.is_valid():
        path = form.save()

        url = '{0}://{1}{2}'.format(
            request.scheme,
            request.get_host(),
            path,
        )
        return JsonResponse({'url': url})

    return HttpResponseBadRequest()
