from unittest import mock
from django.test import TestCase, Client
from django.test.utils import override_settings
from django.contrib.auth.hashers import make_password
from django.contrib.auth.models import Permission
from django.core.signing import SignatureExpired, dumps
from django.urls import reverse, resolve
from django.core import mail
from registration.tests.factories import UserFactory, UserModel
from registration import views
import random, string

class RegistrationView(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

    def setUp(self):
        self.client = Client()
        self.password = 'password'

    def chk_class(self, resolver, class_view):
        self.assertEqual(resolver.func.__name__, class_view.__name__)

    def create_random_password_for_test(self, length=16):
        data = string.ascii_uppercase + string.ascii_lowercase + string.digits + '%&$#()'
        password = ''.join(random.sample(data, length))

        return password

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()

class TopPageViewTests(RegistrationView):
    def test_top_page_access(self):
        url = reverse('registration:top_page')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed('registration/top_page.html')

    def test_top_page_view(self):
        resolver = resolve('/')
        self.chk_class(resolver, views.TopPage)

class LoginPageTests(RegistrationView):
    def setUp(self):
        super().setUp()
        self.user = UserFactory(username='user', password=make_password(self.password))

    def test_valid_login_page_access(self):
        # check username
        params = {
            'username': self.user.username,
            'password': self.password,
        }
        url = reverse('registration:login')
        response = self.client.post(url, params, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed('registration/login.html')
        self.assertTrue(response.context['user'].is_authenticated)
        self.client.logout()

        # check email
        params = {
            'username': self.user.email,
            'password': self.password,
        }
        url = reverse('registration:login')
        response = self.client.post(url, params, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed('registration/login.html')
        self.assertTrue(response.context['user'].is_authenticated)
        self.client.logout()

    def test_login_page_view(self):
        resolver = resolve('/login/')
        self.chk_class(resolver, views.LoginPage)
        self.client.logout()

    @override_settings(AXES_ENABLED=False)
    def test_invalid_username_login_page_access(self):
        # check username
        params = {
            'username': self.user.username + '0',
            'password': self.password,
        }
        url = reverse('registration:login')
        response = self.client.post(url, params)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed('registration/login.html')
        self.assertFalse(response.context['user'].is_authenticated)

    @override_settings(AXES_ENABLED=False)
    def test_invalid_password_login_page_access(self):
        # check username
        params = {
            'username': self.user.username,
            'password': self.password + '0',
        }
        url = reverse('registration:login')
        response = self.client.post(url, params)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed('registration/login.html')
        self.assertFalse(response.context['user'].is_authenticated)

class LoginedView(RegistrationView):
    @override_settings(AXES_ENABLED=False)
    def setUp(self):
        super().setUp()
        self.user = UserFactory(username='user', password=make_password(self.password))
        self.client.login(username=self.user.username, password=self.password)

class LogoutPageTests(LoginedView):
    def test_logout_page_access(self):
        url = reverse('registration:logout')
        response = self.client.post(url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed('registration/top_page.html')
        self.assertFalse(response.context['user'].is_authenticated)

    def test_logout_page_view(self):
        resolver = resolve('/logout/')
        self.chk_class(resolver, views.LogoutPage)

class ExistStaffAndSuperuserView(RegistrationView):
    def setUp(self):
        super().setUp()
        self.user = UserFactory(username='user', password=make_password(self.password))
        self.staffuser = UserFactory(username='staffuser', password=make_password(self.password), is_staff=True, is_superuser=False)
        self.superuser = UserFactory(username='superuser', password=make_password(self.password), is_staff=True, is_superuser=True)

class AccountsPageTests(ExistStaffAndSuperuserView):
    @override_settings(AXES_ENABLED=False)
    def setUp(self):
        super().setUp()
        self.client.login(username=self.superuser.username, password=self.password)
        self.url = reverse('registration:accounts_page')

    def test_valid_accouts_page_access(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed('registration/account_list.html')
        self.assertTrue(response.context['user'].is_authenticated)
        self.assertTrue(response.context['user'].is_superuser)

    def test_accouts_page_view(self):
        resolver = resolve('/accounts_page/')
        self.chk_class(resolver, views.AccountsPage)

    def test_invalid_no_login_account_page_access(self):
        self.client.logout()
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 403)
        self.assertFalse(response.context['user'].is_authenticated)

    @override_settings(AXES_ENABLED=False)
    def test_invalid_is_default_user_account_page_access(self):
        self.client.logout()
        self.client.login(username=self.user.username, password=self.password)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 403)
        self.assertTrue(response.context['user'].is_authenticated)
        self.assertFalse(response.context['user'].is_superuser)

    @override_settings(AXES_ENABLED=False)
    def test_invalid_is_not_superuser_account_page_access(self):
        self.client.logout()
        self.client.login(username=self.staffuser.username, password=self.password)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 403)
        self.assertTrue(response.context['user'].is_authenticated)
        self.assertFalse(response.context['user'].is_superuser)

class UpdateUserStatusTest(ExistStaffAndSuperuserView):
    @override_settings(AXES_ENABLED=False)
    def setUp(self):
        super().setUp()
        self.client.login(username=self.superuser.username, password=self.password)
        params = {
            'pk': self.user.pk,
        }
        self.url = reverse('registration:update_user_status', kwargs=params)

    def test_valid_update_user_status_access(self):
        response = self.client.post(self.url, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed('registration/account_list.html')
        self.assertTrue(response.context['user'].is_authenticated)
        self.assertTrue(response.context['user'].is_superuser)
        _user = UserModel.objects.get(pk=self.user.pk)
        self.assertFalse(_user.is_active)

    def test_update_user_status_view(self):
        resolver = resolve('/update/{}/'.format(self.user.pk))
        self.chk_class(resolver, views.UpdateUserStatus)

    def test_invalid_no_login_update_user_status_access(self):
        self.client.logout()
        response = self.client.post(self.url)
        self.assertEqual(response.status_code, 403)
        self.assertFalse(response.context['user'].is_authenticated)
        _user = UserModel.objects.get(pk=self.user.pk)
        self.assertTrue(_user.is_active)

    @override_settings(AXES_ENABLED=False)
    def test_invalid_is_default_user_update_user_status_access(self):
        self.client.logout()
        self.client.login(username=self.user.username, password=self.password)
        response = self.client.post(self.url)
        self.assertEqual(response.status_code, 403)
        self.assertTrue(response.context['user'].is_authenticated)
        _user = UserModel.objects.get(pk=self.user.pk)
        self.assertTrue(_user.is_active)

    @override_settings(AXES_ENABLED=False)
    def test_invalid_is_not_superuser_account_page_access(self):
        self.client.logout()
        self.client.login(username=self.staffuser.username, password=self.password)
        response = self.client.post(self.url)
        self.assertEqual(response.status_code, 403)
        self.assertTrue(response.context['user'].is_authenticated)
        _user = UserModel.objects.get(pk=self.user.pk)
        self.assertTrue(_user.is_active)

class DeleteUserPageTests(ExistStaffAndSuperuserView):
    @override_settings(AXES_ENABLED=False)
    def setUp(self):
        super().setUp()
        self.client.login(username=self.superuser.username, password=self.password)
        self.test_user = UserFactory(username='test_user', is_active=False)
        params = {
            'pk': self.test_user.pk,
        }
        self.url = reverse('registration:delete_user_page', kwargs=params)

    def test_valid_delete_user_page_access(self):
        response = self.client.post(self.url, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.context['user'].is_authenticated)
        self.assertTrue(response.context['user'].is_superuser)
        with self.assertRaises(UserModel.DoesNotExist):
            _ = UserModel.objects.get(pk=self.test_user.pk)

    def test_valid_get_request_delete_user_page_access(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 403)

    def test_valid_delete_user_page_view(self):
        resolver = resolve('/delete/{}/'.format(self.user.pk))
        self.chk_class(resolver, views.DeleteUserPage)

    def test_invalid_no_login_delete_user_page_access(self):
        self.client.logout()
        response = self.client.post(self.url)
        self.assertEqual(response.status_code, 403)
        self.assertFalse(response.context['user'].is_authenticated)
        _user = UserModel.objects.get(pk=self.test_user.pk)

    @override_settings(AXES_ENABLED=False)
    def test_invalid_is_default_user_delete_user_page_access(self):
        self.client.logout()
        self.client.login(username=self.user.username, password=self.password)
        response = self.client.post(self.url)
        self.assertEqual(response.status_code, 403)
        self.assertTrue(response.context['user'].is_authenticated)
        _ = UserModel.objects.get(pk=self.test_user.pk)

    @override_settings(AXES_ENABLED=False)
    def test_invalid_is_not_delete_user_page_access(self):
        self.client.logout()
        self.client.login(username=self.staffuser.username, password=self.password)
        response = self.client.post(self.url)
        self.assertEqual(response.status_code, 403)
        self.assertTrue(response.context['user'].is_authenticated)
        _ = UserModel.objects.get(pk=self.test_user.pk)

class CreateUserTests(RegistrationView):
    def setUp(self):
        super().setUp()
        self.user = UserFactory(username='user', is_active=False)
        self.password = self.create_random_password_for_test()

    def test_valid_create_user_access(self):
        username = 'test_user'
        params = {
            'username': username,
            'email': '{}@example.com'.format(username),
            'viewname': '_{}'.format(username),
            'password1': self.password,
            'password2': self.password,
        }
        url = reverse('registration:create_user')
        response = self.client.post(url, params)
        self.assertRedirects(response, reverse('registration:create_user_done'), status_code=302, target_status_code=200, msg_prefix='', fetch_redirect_response=True)
        self.assertTemplateUsed('registration/create_user.html')
        _user = UserModel.objects.get(username=username)
        self.assertFalse(_user.is_active)
        self.assertEqual(len(mail.outbox), 1)

    def test_valid_create_user_done_access(self):
        url = reverse('registration:create_user_done')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_valid_create_user_view(self):
        resolver = resolve('/create_user/')
        self.chk_class(resolver, views.CreateUser)

    def test_valid_create_user_done_view(self):
        resolver = resolve('/create_user/done/')
        self.chk_class(resolver, views.CreateUserDone)

    def test_valid_create_user_complete_access(self):
        params = {
            'token': dumps(self.user.pk)
        }
        url = reverse('registration:create_user_complete', kwargs=params)
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        _user = UserModel.objects.get(pk=self.user.pk)
        self.assertTrue(_user.is_active)
        self.assertTrue(_user.has_perm('registration.view_user'))
        self.assertTrue(_user.has_perm('auth.view_permission'))

    def test_valid_create_user_complete_view(self):
        resolver = resolve('/create_user/complete/{}/'.format('123'))
        self.chk_class(resolver, views.CreateUserComplete)

    def test_invalid_bad_signature_create_user_complete_view(self):
        params = {
            'token': dumps(self.user.pk) + 'dummy'
        }
        url = reverse('registration:create_user_complete', kwargs=params)
        response = self.client.get(url)
        self.assertEqual(response.status_code, 400)
        _user = UserModel.objects.get(pk=self.user.pk)
        self.assertFalse(_user.is_active)

    @mock.patch('django.core.signing.TimestampSigner.unsign', side_effect=SignatureExpired)
    def test_invalid_signature_expired_create_user_complete_view(self, _):
        params = {
            'token': dumps(self.user.pk)
        }
        url = reverse('registration:create_user_complete', kwargs=params)
        response = self.client.get(url)
        self.assertEqual(response.status_code, 400)
        _user = UserModel.objects.get(pk=self.user.pk)
        self.assertFalse(_user.is_active)

    def test_invalid_user_doesnot_exist_create_user_complete_view(self):
        params = {
            'token': dumps(UserModel.objects.count() + 1)
        }
        url = reverse('registration:create_user_complete', kwargs=params)
        response = self.client.get(url)
        self.assertEqual(response.status_code, 400)
        _user = UserModel.objects.get(pk=self.user.pk)
        self.assertFalse(_user.is_active)

    def test_invalid_active_user_create_user_complete_view(self):
        _active_user = UserFactory(username='active_user')
        params = {
            'token': dumps(_active_user.pk)
        }
        url = reverse('registration:create_user_complete', kwargs=params)
        response = self.client.get(url)
        self.assertEqual(response.status_code, 400)
        _active_user = UserModel.objects.get(pk=_active_user.pk)
        self.assertTrue(_active_user.is_active)
