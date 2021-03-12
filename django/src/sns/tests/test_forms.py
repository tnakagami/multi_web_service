from django.test import TestCase
from registration.tests.factories import UserFactory, UserModel
from sns import forms, models

class SNSForm(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

    @classmethod
    def setUpTestData(cls):
        cls.owner = UserFactory()
        cls.follower = UserFactory()

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()

class TweetFormTests(SNSForm):
    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        cls.model = models.Tweet
        cls.form = forms.CreateTweetForm

    def test_valid_form(self):
        text = 'abc'
        data = {
            'text': text,
        }
        tweet = self.model()
        form = self.form(data, instance=tweet)
        self.assertTrue(form.is_valid())
        form.clean()
        self.assertEqual(text, form.cleaned_data['text'])

    def test_valid_form_text_length_is_140(self):
        text = 'a' * 140
        data = {
            'text': text,
        }
        tweet = self.model()
        form = self.form(data, instance=tweet)
        self.assertTrue(form.is_valid())
        form.clean()
        self.assertEqual(text, form.cleaned_data['text'])

    def test_invalid_form_data_is_empty(self):
        data = {}
        tweet = self.model()
        form = self.form(data, instance=tweet)
        self.assertFalse(form.is_valid())

    def test_invalid_form_text_is_too_short(self):
        text = ''
        data = {
            'text': text
        }
        tweet = self.model()
        form = self.form(data, instance=tweet)
        self.assertFalse(form.is_valid())

    def test_invalid_form_text_is_too_long(self):
        text = 'a' * 141
        data = {
            'text': text
        }
        tweet = self.model()
        form = self.form(data, instance=tweet)
        self.assertFalse(form.is_valid())

class RelationshipFormTests(SNSForm):
    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        cls.model = models.Relationship
        cls.form = forms.CreateRelationshipForm

    def test_valid_form(self):
        data = {
            'owner_id': self.owner.pk,
            'follower_id': self.follower.pk,
        }
        relationship = self.model()
        form = self.form(data, instance=relationship)
        self.assertTrue(form.is_valid())

    def test_invalid_form_data_is_empty(self):
        data = {}
        relationship = self.model()
        form = self.form(data, instance=relationship)
        self.assertFalse(form.is_valid())
