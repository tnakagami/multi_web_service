from django.test import TestCase
from registration.tests.factories import UserFactory
from registration import forms

class RegstrationFormTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

    def test_update_user_status_form(self):
        params = {
            'is_active': False
        }
        form = forms.UpdateUserStatusForm(params)
        self.assertTrue(form.is_valid())

    def test_update_account_info_form(self):
        params = {
            'viewname': 'c',
        }
        form = forms.UpdateAccountInfoForm(params)
        self.assertTrue(form.is_valid())

        params = {
            'viewname': '',
        }
        form = forms.UpdateAccountInfoForm(params)
        self.assertTrue(form.is_valid())

    def test_valid_change_email_form(self):
        params = {
            'email': 'alice@example.com',
        }
        form = forms.ChangeEmailForm(params)
        self.assertTrue(form.is_valid())

    def test_invalid_change_email_form(self):
        params = {
            'email': 'alice.example.com',
        }
        form = forms.ChangeEmailForm(params)
        self.assertFalse(form.is_valid())

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
