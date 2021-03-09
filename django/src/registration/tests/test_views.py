from django.test import TestCase, Client
from django.test.utils import override_settings
from django.contrib.auth.hashers import make_password
from django.urls import reverse, resolve
from registration.tests.factories import UserFactory, UserModel
from registration import views

class RegistrationView(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

    def setUp(self):
        self.client = Client()
        self.password = 'password'

    def chk_class(self, resolver, class_view):
        self.assertEqual(resolver.func.__name__, class_view.__name__)

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

    def test_valid_accouts_page_access(self):
        url = reverse('registration:accounts_page')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed('registration/account_list.html')
        self.assertTrue(response.context['user'].is_authenticated)
        self.assertTrue(response.context['user'].is_superuser)

    def test_accouts_page_view(self):
        resolver = resolve('/accounts_page/')
        self.chk_class(resolver, views.AccountsPage)

    def test_invalid_no_login_account_page_access(self):
        self.client.logout()
        url = reverse('registration:accounts_page')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 403)
        self.assertFalse(response.context['user'].is_authenticated)

    @override_settings(AXES_ENABLED=False)
    def test_invalid_is_default_user_account_page_access(self):
        self.client.logout()
        self.client.login(username=self.user.username, password=self.password)
        url = reverse('registration:accounts_page')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 403)
        self.assertTrue(response.context['user'].is_authenticated)
        self.assertFalse(response.context['user'].is_superuser)

    @override_settings(AXES_ENABLED=False)
    def test_invalid_is_not_superuser_account_page_access(self):
        self.client.logout()
        self.client.login(username=self.staffuser.username, password=self.password)
        url = reverse('registration:accounts_page')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 403)
        self.assertTrue(response.context['user'].is_authenticated)
        self.assertFalse(response.context['user'].is_superuser)
