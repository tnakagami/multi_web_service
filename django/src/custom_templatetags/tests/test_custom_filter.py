from django.test import TestCase
from custom_templatetags import custom_filter
from django.contrib.auth.models import Permission, Group
from registration.tests.factories import UserFactory

class CustomFilter(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

    @classmethod
    def setUpTestData(cls):
        cls.users = UserFactory.create_batch(4)
        codename = 'view_user'
        cls.group_name = 'editors'
        cls.permission_name = 'registration.{}'.format(codename)
        group = Group.objects.create(name=cls.group_name)
        view_user = Permission.objects.get(codename=codename)
        # user0: have both no permission and no group
        # user1: have only permission
        # user2: have only group
        # user3: have both permission and group
        cls.users[1].user_permissions.add(view_user)
        cls.users[2].groups.add(group)
        cls.users[3].user_permissions.add(view_user)
        cls.users[3].groups.add(group)

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()

class HasGroupTests(CustomFilter):
    def test_chk_user0_group(self):
        self.assertFalse(custom_filter.has_group(self.users[0], self.group_name))
    def test_chk_user1_group(self):
        self.assertFalse(custom_filter.has_group(self.users[1], self.group_name))
    def test_chk_user2_group(self):
        self.assertTrue(custom_filter.has_group(self.users[2], self.group_name))
    def test_chk_user3_group(self):
        self.assertTrue(custom_filter.has_group(self.users[3], self.group_name))

class HasPermTests(CustomFilter):
    def test_chk_user0_permission(self):
        self.assertFalse(custom_filter.has_perm(self.users[0], self.permission_name))
    def test_chk_user1_permission(self):
        self.assertTrue(custom_filter.has_perm(self.users[1], self.permission_name))
    def test_chk_user2_permission(self):
        self.assertFalse(custom_filter.has_perm(self.users[2], self.permission_name))
    def test_chk_user3_permission(self):
        self.assertTrue(custom_filter.has_perm(self.users[3], self.permission_name))
