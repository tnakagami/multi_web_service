from django.test import TestCase
from registration.tests.factories import UserFactory

# sample
class UserModelTests(TestCase):
    def setUp(self):
        self.normal_user = UserFactory()
        self.blank_viewname_user = UserFactory(viewname='')

    def test_create_valid_user(self):
        self.assertEqual(self.normal_user.username, 'user0')
        self.assertEqual(self.normal_user.viewname, 'viewname0')
        self.assertEqual(self.normal_user.email, 'user0@example.com')
        self.assertFalse(self.normal_user.is_staff)
        self.assertTrue(self.normal_user.is_active)

    def test_create_valid_user_blank_viewname(self):
        self.assertEqual(self.blank_viewname_user.viewname, '')
