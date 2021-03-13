from django.contrib.auth import get_user_model
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin, AccessMixin
from django.shortcuts import redirect, get_object_or_404
from django.urls import reverse_lazy, reverse
from django.http import Http404, JsonResponse, HttpResponseBadRequest
from django.views.generic import ListView, CreateView, UpdateView, DeleteView, DetailView
from django.db.models import Q
from . import models, forms

User = get_user_model()

class OnlyYouMixin(UserPassesTestMixin):
    raise_exception = True

    def test_func(self):
        user = self.request.user
        # Check primary key of user is equivalent or user is superuser
        chk_account = user.pk == self.kwargs['pk'] or user.is_superuser
        # Check permission
        chk_perm = user.has_perm('registration.view_user') and user.has_perm('auth.view_permission')
        ret = chk_account and chk_perm

        return ret

class PostListView(LoginRequiredMixin, ListView):
    """
    public blog list
    """
    model = models.Post
    template_name = 'blog/index.html'
    paginate_by = 10
    context_object_name = 'posts'

    def get_queryset(self):
        queryset = super().get_queryset().filter(Q(is_public=True) | Q(user=self.request.user))
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

class OwnPostListView(OnlyYouMixin, ListView):
    model = models.Post
    template_name = 'blog/own_post.html'
    paginate_by = 10
    context_object_name = 'posts'

    def get_queryset(self):
        queryset = super().get_queryset().filter(user=self.request.user)
        form = forms.PostSearchForm(self.request.GET or None)

        # check form
        if form.is_valid():
            queryset = form.filtered_queryset(queryset)
        # ordering
        queryset = queryset.order_by('-updated_at').prefetch_related('tags')

        return queryset

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        context['search_form'] = forms.PostSearchForm(self.request.GET or None, user=self.request.user)

        return context

class OwnTagListView(OnlyYouMixin, ListView):
    model = models.Tag
    template_name = 'blog/own_tag.html'
    paginate_by = 10
    context_object_name = 'tags'

    def get_queryset(self):
        queryset = super().get_queryset().filter(user=self.request.user)
        form = forms.TagSearchForm(self.request.GET or None)

        # check form
        if form.is_valid():
            queryset = form.filtered_queryset(queryset)
        # ordering
        queryset = queryset.order_by('-name')

        return queryset

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        context['search_form'] = forms.TagSearchForm(self.request.GET or None)

        return context

class TagCreateView(LoginRequiredMixin, CreateView):
    raise_exception = True
    model = models.Tag
    form_class = forms.TagForm
    template_name = 'blog/tag_create_form.html'
    success_url = reverse_lazy('blog:index')

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user

        return kwargs

    def form_valid(self, form):
        instance = form.save(commit=False)
        instance.user = self.request.user
        instance.save()

        return super().form_valid(form)

class TagUpdateView(AccessMixin, UpdateView):
    raise_exception = True
    model = models.Tag
    form_class = forms.TagForm
    template_name = 'blog/tag_update_form.html'

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user

        return kwargs

    def dispatch(self, request, *args, **kwargs):
        try:
            tag = self.model.objects.get(pk=kwargs['pk'])
        except Exception:
            raise Http404

        # if user is not authenticated or tag is not request user's
        if not request.user.is_authenticated or request.user.pk != tag.user.pk:
            return self.handle_no_permission()
        # checks pass let http method handlers process the request
        return super().dispatch(request, *args, **kwargs)

    def get_success_url(self):
        return reverse('blog:own_tag', kwargs={'pk': self.request.user.pk})

class TagDeleteView(AccessMixin, DeleteView):
    raise_exception = True
    model = models.Tag

    def get(self, request, *args, **kwargs):
        # ignore direct access
        return self.handle_no_permission()

    def dispatch(self, request, *args, **kwargs):
        try:
            tag = self.model.objects.get(pk=kwargs['pk'])
        except Exception:
            raise Http404

        # if user is not authenticated or tag is not request user's
        if not request.user.is_authenticated or request.user.pk != tag.user.pk:
            return self.handle_no_permission()
        # checks pass let http method handlers process the request
        return super().dispatch(request, *args, **kwargs)

    def get_success_url(self):
        return reverse('blog:own_tag', kwargs={'pk': self.request.user.pk})

class PostCreateView(LoginRequiredMixin, CreateView):
    raise_exception = True
    model = models.Post
    form_class = forms.PostForm
    template_name = 'blog/post_create_form.html'
    success_url = reverse_lazy('blog:index')

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user

        return kwargs

    def form_valid(self, form):
        instance = form.save(commit=False)
        instance.user = self.request.user
        instance.save()

        return super().form_valid(form)

class PostUpdateView(AccessMixin, UpdateView):
    raise_exception = True
    model = models.Post
    form_class = forms.PostForm
    template_name = 'blog/post_update_form.html'

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        kwargs['pk'] = self.kwargs['pk']

        return kwargs

    def dispatch(self, request, *args, **kwargs):
        try:
            post = self.model.objects.get(pk=kwargs['pk'])
        except Exception:
            raise Http404

        # if user is not authenticated or post is not request user's
        if not request.user.is_authenticated or request.user.pk != post.user.pk:
            return self.handle_no_permission()
        # checks pass let http method handlers process the request
        return super().dispatch(request, *args, **kwargs)

    def get_success_url(self):
        return reverse('blog:own_post', kwargs={'pk': self.request.user.pk})

class PostDeleteView(AccessMixin, DeleteView):
    raise_exception = True
    model = models.Post

    def get(self, request, *args, **kwargs):
        # ignore direct access
        return self.handle_no_permission()

    def dispatch(self, request, *args, **kwargs):
        try:
            post = self.model.objects.get(pk=kwargs['pk'])
        except Exception:
            raise Http404

        # if user is not authenticated or post is not request user's
        if not request.user.is_authenticated or request.user.pk != post.user.pk:
            return self.handle_no_permission()
        # checks pass let http method handlers process the request
        return super().dispatch(request, *args, **kwargs)

    def get_success_url(self):
        return reverse('blog:own_post', kwargs={'pk': self.request.user.pk})

class PostDetailView(LoginRequiredMixin, DetailView):
    raise_exception = True
    model = models.Post
    template_name = 'blog/post_detail.html'

    def get_object(self, queryset=None):
        post = super().get_object()

        if post.is_public or post.user.pk == self.request.user.pk:
            return post
        else:
            return self.handle_no_permission()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['comment_form'] = forms.CommentForm()
        context['reply_form'] = forms.ReplyForm()

        return context

class CommentCreateView(LoginRequiredMixin, CreateView):
    model = models.Comment
    form_class = forms.CommentForm

    def get(self, request, *args, **kwargs):
        return self.handle_no_permission()

    def form_valid(self, form):
        post_pk = self.kwargs['pk']
        post = get_object_or_404(models.Post, pk=post_pk)
        comment = form.save(commit=False)
        comment.target = post
        comment.save()

        return redirect('blog:post_detail', pk=post_pk)

class ReplyCreateView(LoginRequiredMixin, CreateView):
    model = models.Reply
    form_class = forms.ReplyForm

    def get(self, request, *args, **kwargs):
        return self.handle_no_permission()

    def form_valid(self, form):
        comment = get_object_or_404(models.Comment, pk=self.kwargs['pk'])
        reply = form.save(commit=False)
        reply.target = comment
        reply.save()

        return redirect('blog:post_detail', pk=comment.target.pk)

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
