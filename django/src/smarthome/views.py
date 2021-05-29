from django.contrib.auth.mixins import UserPassesTestMixin
from django.shortcuts import redirect
from django.urls import reverse_lazy, reverse
from django.urls.exceptions import NoReverseMatch
from django.views.generic import ListView, CreateView
from django.http import Http404, HttpResponse
from . import models, forms

class OnlyStaffUserMixin(UserPassesTestMixin):
    raise_exception = True

    def test_func(self):
        # Check user is staff user
        return self.request.user.is_staff

class IndexView(OnlyStaffUserMixin, ListView):
    """
    Index
    """
    model = models.AccessToken
    template_name = 'smarthome/index.html'
    paginate_by = 10
    queryset = models.AccessToken.objects.order_by('-created_at')
    context_object_name = 'access_tokens'

class AccessTokenCreateView(OnlyStaffUserMixin, CreateView):
    """
    Create access token
    """
    model = models.AccessToken
    form_class = forms.AccessTokenForm
    template_name = 'smarthome/create_access_token.html'
    success_url = reverse_lazy('smarthome:index')

    def form_valid(self, form):
        form.save()
        # 最初のtop_n個だけ残して残りを削除
        top_n = 3
        try:
            filtered_pks = self.model.objects.order_by('-created_at').values_list('pk')[top_n:]
            targets = [data[0] for data in filtered_pks]
            self.model.objects.filter(pk__in=targets).delete()
        except IndexError:
            pass

        return super().form_valid(form)

def get_access_url(request, method='dummy', token=''):
    if request.method == 'GET':
        try:
            uri = reverse('smarthome:{}'.format(method), kwargs={'token': token})
            access_url = '{}://{}{}'.format(request.scheme, request.get_host(), uri)

            return HttpResponse(access_url, content_type='text/plain; charset=utf-8')
        except NoReverseMatch:
            raise Http404('Invalid method name')

    raise Http404('Invalid access')

def open_entrance(request, token):
    if request.method == 'GET':
        target = models.AccessToken.objects.order_by('-created_at').first()

        if target.is_valid_access_token(token):
            url = 'http://analyzer.localnet.jp:1880/curtain'
            data = {'payload': 'open'}
            target.send_post_request(url, data)

            return redirect('registration:top_page')

    raise Http404('Invalid access')
