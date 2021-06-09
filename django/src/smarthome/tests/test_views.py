from unittest import mock
from django.test import TestCase
from django.test.utils import override_settings
from django.contrib.auth.hashers import make_password
from django.urls import reverse, resolve
from registration.tests.factories import UserFactory
from requests.models import Response
from smarthome.tests.factories import AccessTokenFactory
from smarthome import views, models
from websocket._exceptions import WebSocketTimeoutException, WebSocketConnectionClosedException

class SmartHomeView(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

    @classmethod
    def setUpTestData(cls):
        cls.password = 'password'
        cls.user = UserFactory(username='user', password=make_password(cls.password))
        cls.staffuser = UserFactory(username='staffuser', password=make_password(cls.password), is_staff=True, is_superuser=False)

    def chk_class(self, resolver, class_view):
        self.assertEqual(resolver.func.__name__, class_view.__name__)

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()

class IndexViewTests(SmartHomeView):
    @override_settings(AXES_ENABLED=False)
    def setUp(self):
        self.client.login(username=self.staffuser.username, password=self.password)
        self.url = reverse('smarthome:index')

    def test_resolve_url(self):
        resolver = resolve('/smarthome/')
        self.chk_class(resolver, views.IndexView)

    def test_no_login_access(self):
        self.client.logout()
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 403)

    @override_settings(AXES_ENABLED=False)
    def test_normal_user_login_access(self):
        self.client.logout()
        self.client.login(username=self.user.username, password=self.password)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 403)

    def test_listed_10tokens(self):
        AccessTokenFactory.create_batch(10)
        response = self.client.get(self.url)
        self.assertTemplateUsed('smarthome/index.html')
        self.assertEqual(response.status_code, 200)
        self.assertTrue('access_tokens' in response.context.keys())
        self.assertTrue('paginator' in response.context.keys())
        _access_tokens = response.context.get('access_tokens')
        _paginator = response.context.get('paginator')
        self.assertEqual(_access_tokens.count(), 10)
        self.assertEqual(_paginator.page_range[-1], 1)

    def test_listed_11tokens(self):
        AccessTokenFactory.create_batch(11)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        _access_tokens = response.context.get('access_tokens')
        _paginator = response.context.get('paginator')
        self.assertEqual(_access_tokens.count(), 10)
        self.assertEqual(_paginator.page_range[-1], 2)

    def test_chk_pagination(self):
        AccessTokenFactory.create_batch(23)
        data = {
            'page': 3,
        }
        response = self.client.get(self.url, data)
        self.assertEqual(response.status_code, 200)
        self.assertTrue('access_tokens' in response.context.keys())
        _posts = response.context.get('access_tokens')
        self.assertEqual(_posts.count(), 3) # 23 % 10: total_access_token_count % paginate_by

class AccessTokenCreateView(SmartHomeView):
    @override_settings(AXES_ENABLED=False)
    def setUp(self):
        self.client.login(username=self.staffuser.username, password=self.password)
        self.url = reverse('smarthome:create_access_token')

    def test_resolve_url(self):
        resolver = resolve('/smarthome/create/access_token')
        self.chk_class(resolver, views.AccessTokenCreateView)

    def test_no_login_access(self):
        self.client.logout()
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 403)

    @override_settings(AXES_ENABLED=False)
    def test_normal_user_login_access(self):
        self.client.logout()
        self.client.login(username=self.user.username, password=self.password)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 403)

    def test_chk_access_token_form(self):
        response = self.client.get(self.url)
        self.assertTemplateUsed('smarthome/create_access_token.html')
        self.assertEqual(response.status_code, 200)
        self.assertTrue('form' in response.context.keys())

    def test_create_access_token(self):
        data = {
            'access_token': 'sample10ken'
        }
        response = self.client.post(self.url, data, follow=True)
        self.assertEqual(response.status_code, 200)
        _access_token = models.AccessToken.objects.all().last()
        self.assertEqual(_access_token.access_token, data['access_token'])
        self.assertEqual(models.AccessToken.objects.count(), 1)

    def test_create_access_token_and_delete_access_token(self):
        AccessTokenFactory.create_batch(3)
        data = {
            'access_token': 'sample10ken'
        }
        response = self.client.post(self.url, data, follow=True)
        self.assertEqual(response.status_code, 200)
        _access_token = models.AccessToken.objects.all().last()
        self.assertEqual(_access_token.access_token, data['access_token'])
        self.assertEqual(models.AccessToken.objects.count(), 3)

class GenerateToken(SmartHomeView):
    @override_settings(AXES_ENABLED=False)
    def setUp(self):
        self.client.login(username=self.staffuser.username, password=self.password)
        self.url = reverse('smarthome:generate_token')

    def test_resolve_url(self):
        resolver = resolve('/smarthome/generate/token')
        self.chk_class(resolver, views.GenerateTokenView)

    def test_no_login_access(self):
        self.client.logout()
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 403)

    @override_settings(AXES_ENABLED=False)
    def test_normal_user_login_access(self):
        self.client.logout()
        self.client.login(username=self.user.username, password=self.password)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 403)

    def test_error_post_request(self):
        data = {}
        response = self.client.post(self.url, data, follow=True)
        self.assertEqual(response.status_code, 403)

    @mock.patch('smarthome.views.secrets.token_urlsafe', return_value='sample10ken')
    def test_valid_access_token(self, _):
        response = self.client.get(self.url)
        self.assertEqual('sample10ken', response.content.decode())

class GetAccessUrl(SmartHomeView):
    def setUp(self):
        self.token = 'sample10ken'

    def test_resolve_url(self):
        resolver = resolve('/smarthome/get/url/open_entrance/{}'.format(self.token))
        self.assertEqual(resolver.func, views.get_access_url)

    def test_error_post_request(self):
        data = {}
        url = reverse('smarthome:get_access_url', kwargs={'method': 'open_entrance', 'token': self.token})
        response = self.client.post(url, data, follow=True)
        self.assertEqual(response.status_code, 404)

    def test_invalid_method(self):
        url = reverse('smarthome:get_access_url', kwargs={'method': 'not_exist_url_name', 'token': self.token})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)

    def test_valid_url(self):
        url = reverse('smarthome:get_access_url', kwargs={'method': 'open_entrance', 'token': self.token})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertTrue('/smarthome/open/entrance/{}'.format(self.token) in response.content.decode())

class MockWebSocket:
    def __init__(self):
        pass
    def send(self, data):
        pass
    def recv(self):
        return ''
    def close(self):
        pass

class OpenEntranceFuncTests(SmartHomeView):
    def setUp(self):
        self.token = 'target10ken'
        self.exact_token = AccessTokenFactory(access_token=self.token)

    def test_resolve_url(self):
        resolver = resolve('/smarthome/open/entrance/{}'.format(self.token))
        self.assertEqual(resolver.func, views.open_entrance)

    def test_error_post_request(self):
        data = {}
        url = reverse('smarthome:open_entrance', kwargs={'token': self.token})
        response = self.client.post(url, data, follow=True)
        self.assertEqual(response.status_code, 404)

    def test_invalid_access_token(self):
        url = reverse('smarthome:open_entrance', kwargs={'token': 'dummy'})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)

    @mock.patch('smarthome.models.create_connection') # second
    @mock.patch('smarthome.models.requests.get') # first
    def test_valid_access_token(self, mock_get_method, mock_ws_method):
        class _WebSocket(MockWebSocket):
            def recv(self):
                return '{"status_code": 200, "message": "ok"}'
        # first
        mock_response = Response()
        mock_response.status_code = 200
        mock_response._content = b'{"device":"00:11:22:33:44:55","command":"press","message":"none"}'
        mock_get_method.return_value = mock_response
        # second
        mock_ws_method.return_value = _WebSocket()
        url = reverse('smarthome:open_entrance', kwargs={'token': self.token})
        response = self.client.get(url)
        self.assertEqual('status code: 200, msg: ok', response.content.decode())

    @mock.patch('smarthome.models.create_connection') # second
    @mock.patch('smarthome.models.requests.get') # first
    def test_websocket_timeout_exception(self, mock_get_method, mock_ws_method):
        class _WebSocket(MockWebSocket):
            def recv(self):
                raise WebSocketTimeoutException('Timeout')
        # first
        mock_response = Response()
        mock_response.status_code = 200
        mock_response._content = b'{"device":"00:11:22:33:44:55","command":"press"}'
        mock_get_method.return_value = mock_response
        # second
        mock_ws_method.return_value = _WebSocket()
        url = reverse('smarthome:open_entrance', kwargs={'token': self.token})
        response = self.client.get(url)
        self.assertEqual('status code: 500, msg: Internal Server Error (Timeout)', response.content.decode())

    @mock.patch('smarthome.models.create_connection') # second
    @mock.patch('smarthome.models.requests.get') # first
    def test_websocket_connection_closed_exception(self, mock_get_method, mock_ws_method):
        class _WebSocket(MockWebSocket):
            def recv(self):
                raise WebSocketConnectionClosedException('ConnectionClosed')
        # first
        mock_response = Response()
        mock_response.status_code = 200
        mock_response._content = b'{"device":"00:11:22:33:44:55","command":"press"}'
        mock_get_method.return_value = mock_response
        # second
        mock_ws_method.return_value = _WebSocket()
        url = reverse('smarthome:open_entrance', kwargs={'token': self.token})
        response = self.client.get(url)
        self.assertEqual('status code: 500, msg: Internal Server Error (ConnectionClosed)', response.content.decode())

    @mock.patch('smarthome.models.requests.get')
    def test_raise_get_method_of_requests(self, mock_get_method):
        mock_response = Response()
        mock_response.status_code = 404
        mock_response._content = 'Page Not Found'
        mock_get_method.return_value = mock_response
        url = reverse('smarthome:open_entrance', kwargs={'token': self.token})
        response = self.client.get(url)
        self.assertEqual('status code: 404, msg: Not Found', response.content.decode())

    @mock.patch('smarthome.models.create_connection', side_effect=WebSocketTimeoutException('Connection Timeout'))
    @mock.patch('smarthome.models.requests.get')
    def test_websocket_create_connection_exception(self, mock_get_method, _):
        mock_response = Response()
        mock_response.status_code = 200
        mock_response._content = b'{"device":"00:11:22:33:44:55","command":"press"}'
        mock_get_method.return_value = mock_response
        url = reverse('smarthome:open_entrance', kwargs={'token': self.token})
        response = self.client.get(url)
        self.assertEqual('status code: 404, msg: Not Found', response.content.decode())
