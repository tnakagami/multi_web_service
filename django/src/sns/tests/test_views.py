from unittest import mock
from django.test import TestCase, Client
from django.test.utils import override_settings
from django.urls import reverse, resolve
from registration.tests.factories import UserFactory, UserModel
from sns import views, models

class SNSView(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

    @classmethod
    def setUpTestData(cls):
        cls.users = UserFactory.create_batch(10)
        cls.client = Client()
        cls.owner = cls.users[0]
        cls.password = 'password'

    def chk_class(self, resolver, class_view):
        self.assertEqual(resolver.func.__name__, class_view.__name__)

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()

class TimeLineViewTests(SNSView):
    @override_settings(AXES_ENABLED=False)
    def setUp(self):
        super().setUp()
        self.client.login(username=self.owner.username, password=self.password)
        self.url = reverse('sns:time_line')

    def test_resolve_url(self):
        resolver = resolve('/sns/')
        self.chk_class(resolver, views.TimeLineView)

    def test_valid_no_login_access(self):
        self.client.logout()
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 302)

    def test_valid_no_tweet(self):
        response = self.client.get(self.url)
        self.assertTemplateUsed('sns/time_line.html')
        self.assertEqual(response.status_code, 200)
        self.assertTrue('tweets' in response.context.keys())
        _tweets = response.context.get('tweets')
        self.assertEqual(_tweets.count(), 0)

    def test_valid_create_tweet(self):
        text = 'This is a sample tweet'
        data = {
            'text': text,
        }
        response = self.client.post(self.url, data, follow=True)
        self.assertEqual(response.status_code, 200)
        _tweets = response.context.get('tweets')
        self.assertEqual(_tweets.count(), 1)
        tweet = _tweets.first()
        self.assertEqual(tweet.user, self.owner)
        self.assertEqual(tweet.text, text)

    def __create_tweets(self, ignore_users=None):
        users = self.users
        if ignore_users is not None and isinstance(ignore_users, list):
            users = filter(lambda _user: _user.username not in ignore_users, users)

        for _user in users:
            text = 'I am {}'.format(_user.username)
            tweet = models.Tweet()
            tweet.user = _user
            tweet.text = text
            tweet.save()

    def test_valid_no_other_users_tweet(self):
        self.__create_tweets([self.owner.username])

        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        _tweets = response.context.get('tweets')
        self.assertEqual(_tweets.count(), 0)

    def test_valid_follower_tweet(self):
        self.__create_tweets([self.owner.username])
        follower = self.users[-1]
        relationship = models.Relationship()
        relationship.owner = self.owner
        relationship.follower = follower
        relationship.save()

        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        _tweets = response.context.get('tweets')
        self.assertEqual(_tweets.count(), 1)

    def test_valid_own_tweet_and_follower_tweet(self):
        self.__create_tweets()
        follower = self.users[-1]
        relationship = models.Relationship()
        relationship.owner = self.owner
        relationship.follower = follower
        relationship.save()

        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        _tweets = response.context.get('tweets')
        self.assertEqual(_tweets.count(), 2)
