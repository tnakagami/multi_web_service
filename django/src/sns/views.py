from django.contrib.auth import get_user_model
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin, AccessMixin
from django.contrib.auth.models import Permission
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.http import Http404
from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from django_filters.views import FilterView
from django.db.models import Q
from . import models, forms
from .filters import UserFilter

User = get_user_model()

class TimeLineView(LoginRequiredMixin, CreateView):
    """
    List tweet and create own tweet
    """
    template_name = 'sns/time_line.html'
    form_class = forms.CreateTweetForm
    success_url = reverse_lazy('sns:time_line')

    def get_context_data(self, **kwargs):
        user_pk = self.request.user.pk
        # filter the follow users
        follower_relationship = [element['follower_id'] for element in models.Relationship.objects.filter(owner__pk=user_pk).values()]
        # filter the followed users
        follow_relationship = [element['owner_id'] for element in models.Relationship.objects.filter(follower__pk=user_pk).values()]
        queryset = models.Tweet.objects.filter(Q(user__pk=user_pk) | Q(user__pk__in=follower_relationship) | Q(user__pk__in=follow_relationship))
        kwargs['tweets'] = queryset.order_by('-created')

        return super().get_context_data(**kwargs)

    def form_valid(self, form):
        form.instance.user = self.request.user

        return super().form_valid(form)

class DeleteTweetView(AccessMixin, DeleteView):
    raise_exception = True
    model = models.Tweet
    success_url = reverse_lazy('sns:time_line')

    def get(self, request, *args, **kwargs):
        # ignore direct access
        return self.handle_no_permission()

    def dispatch(self, request, *args, **kwargs):
        try:
            tweet = self.model.objects.get(pk=kwargs['pk'])
        except Exception:
            raise Http404

        # if user is not authenticated or tweet is not request user's
        if not request.user.is_authenticated or request.user.pk != tweet.user.pk:
            return self.handle_no_permission()
        # checks pass let http method handlers process the request
        return super().dispatch(request, *args, **kwargs)

class SearchFollowerView(LoginRequiredMixin, FilterView):
    template_name = 'sns/search_follower.html'
    model = User
    filterset_class = UserFilter

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        context['relationship_form'] = forms.CreateRelationshipForm()
        context['relationships'] = models.Relationship.objects.all()

        return context

class CreateRelationshipView(LoginRequiredMixin, CreateView):
    model = models.Relationship
    form_class = forms.CreateRelationshipForm

    def get(self, request, *args, **kwargs):
        return redirect('sns:search_follower')

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['request_user'] = self.request.user

        return kwargs

    def form_valid(self, form):
        form.save()

        return redirect('sns:search_follower')

    def form_invalid(self, form):
        return redirect('sns:search_follower')

class DeleteRelationshipView(AccessMixin, DeleteView):
    raise_exception = True
    model = models.Relationship
    success_url = reverse_lazy('sns:search_follower')

    def get(self, request, *args, **kwargs):
        # ignore direct access
        return self.handle_no_permission()

    def dispatch(self, request, *args, **kwargs):
        try:
            relationship = self.model.objects.get(pk=kwargs['pk'])
        except Exception:
            raise Http404

        # if user is not authenticated or owner is not request user's
        if not request.user.is_authenticated or request.user.pk != relationship.owner.pk:
            return self.handle_no_permission()
        # checks pass let http method handlers process the request
        return super().dispatch(request, *args, **kwargs)
