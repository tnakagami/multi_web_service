from django.test import TestCase
from smarthome import models, forms

class SmartHomeForm(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()

class AccessTokenFormTests(SmartHomeForm):
    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        cls.model = models.AccessToken
        cls.form = forms.AccessTokenForm

    def test_form(self):
        data = {'access_token': 'target2token'}
        form = self.form(data)
        self.assertTrue(form.is_valid())
