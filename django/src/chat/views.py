from django.contrib.auth.mixins import LoginRequiredMixin, AccessMixin
from django.urls import reverse_lazy, reverse
from django.http import Http404
from django.views.generic import ListView, CreateView, UpdateView, DeleteView, DetailView
from django.core.paginator import Paginator
from . import models, forms

def paginate_query(request, queryset, count):
    paginator = Paginator(queryset, count)
    page = request.GET.get('page')
    page_obj = paginator.get_page(page)

    return paginator, page_obj

class RoomListView(LoginRequiredMixin, ListView):
    """
    View to show the list of rooms
    """
    model = models.Room
    template_name = 'chat/index.html'
    paginate_by = 10
    context_object_name = 'rooms'

    def get_queryset(self):
        queryset = super().get_queryset()
        form = forms.RoomSearchForm(self.request.GET or None)

        # check form
        if form.is_valid():
            queryset = form.filtered_queryset(queryset)
        # ordering
        queryset = queryset.order_by('-created_at')

        return queryset

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        context['search_form'] = forms.RoomSearchForm(self.request.GET or None)

        return context

class RoomCreateView(LoginRequiredMixin, CreateView):
    raise_exception = True
    model = models.Room
    form_class = forms.RoomForm
    template_name = 'chat/room_form.html'
    success_url = reverse_lazy('chat:index')

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user

        return kwargs

    def form_valid(self, form):
        instance = form.save(commit=False)
        instance.owner = self.request.user
        instance.save()

        return super().form_valid(form)

class RoomUpdateView(LoginRequiredMixin, UpdateView):
    raise_exception = True
    model = models.Room
    form_class = forms.RoomForm
    template_name = 'chat/room_form.html'
    success_url = reverse_lazy('chat:index')

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user

        return kwargs

    def dispatch(self, request, *args, **kwargs):
        try:
            room = self.model.objects.get(pk=kwargs['pk'])
        except Exception:
            raise Http404

        # if user is not authenticated or room is not request user's
        if not request.user.is_authenticated or request.user.pk != room.owner.pk:
            return self.handle_no_permission()
        # checks pass let http method handlers process the request
        return super().dispatch(request, *args, **kwargs)

class RoomDeleteView(AccessMixin, DeleteView):
    raise_exception = True
    model = models.Room
    success_url = reverse_lazy('chat:index')

    def get(self, request, *args, **kwargs):
        # ignore direct access
        return self.handle_no_permission()

    def dispatch(self, request, *args, **kwargs):
        try:
            room = self.model.objects.get(pk=kwargs['pk'])
        except Exception:
            raise Http404

        # if user is not authenticated or room is not request user's
        if not request.user.is_authenticated or request.user.pk != room.owner.pk:
            return self.handle_no_permission()
        # checks pass let http method handlers process the request
        return super().dispatch(request, *args, **kwargs)

class ChatRoomDetailView(AccessMixin, DetailView):
    raise_exception = True
    model = models.Room
    template_name = 'chat/chat_room.html'

    def dispatch(self, request, *args, **kwargs):
        try:
            room = self.model.objects.get(pk=kwargs['pk'])
        except Exception:
            raise Http404

        # if user is not assigned
        if not room.is_assigned(request.user):
            return self.handle_no_permission()
        # checks pass let http method handlers process the request
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        messages = models.Message.objects.filter(room=self.object).order_by('-created_at')
        paginator, page_obj = paginate_query(self.request, messages, 20)
        context['paginator'] = paginator
        context['page_obj'] = page_obj

        return context
