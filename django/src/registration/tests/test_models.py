from django.test import TestCase
from django.core import mail
from registration.tests.factories import UserFactory, UserModel

# sample
class UserModelTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

    def setUp(self):
        self.normal_user = UserFactory(username='alice', viewname='_alice')

    def test_create_valid_user(self):
        self.assertEqual(self.normal_user.username, 'alice')
        self.assertEqual(self.normal_user.get_full_name(), 'alice')
        self.assertEqual(self.normal_user.get_short_name(), 'alice')
        self.assertEqual(self.normal_user.viewname, '_alice')
        self.assertEqual(self.normal_user.email, 'alice@example.com')
        self.assertFalse(self.normal_user.is_staff)
        self.assertTrue(self.normal_user.is_active)

    def test_create_valid_user_blank_viewname(self):
        blank_viewname_user = UserFactory(viewname='')
        self.assertEqual(blank_viewname_user.viewname, '')

    def test_create_user(self):
        _user = UserModel.objects.create_user(username='user', email='user@example.com', password='password')
        self.assertTrue(isinstance(_user, UserModel))

    def test_create_superuser(self):
        _user = UserModel.objects.create_superuser(username='superuser1', email='superuser1@example.com', password='admin1password', is_staff=True, is_superuser=True)
        self.assertTrue(isinstance(_user, UserModel))
        self.assertTrue(_user.is_staff)
        self.assertTrue(_user.is_superuser)

        with self.assertRaises(ValueError):
            _ = UserModel.objects.create_superuser(username='superuser2', email='superuser2@example.com', password='admin2password', is_staff=True, is_superuser=False)
        with self.assertRaises(ValueError):
            _ = UserModel.objects.create_superuser(username='superuser3', email='superuser3@example.com', password='admin3password', is_staff=False, is_superuser=True)

    def test_aux_create_user(self):
        with self.assertRaises(ValueError):
            _ = UserModel.objects._create_user(username='', email='dummy@example.com', password='dummy')
        with self.assertRaises(ValueError):
            _ = UserModel.objects._create_user(username='dummy', email='', password='dummy')

    def test_send_mail(self):
        _subject = 'subject name'
        _message = 'sample message'
        self.normal_user.email_user(_subject, _message)
        _outbox = mail.outbox[0]
        self.assertEqual(_outbox.subject, _subject)
        self.assertEqual(_outbox.body, _message)

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
