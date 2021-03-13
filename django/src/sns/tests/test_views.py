from unittest import mock
from django.test import TestCase
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
        cls.owner = cls.users[0]
        cls.candidate_followers = list(filter(lambda _user: cls.owner.pk != _user.pk, cls.users))
        cls.password = 'password'

    def chk_class(self, resolver, class_view):
        self.assertEqual(resolver.func.__name__, class_view.__name__)

    def create_tweets(self, ignore_users=None):
        users = self.users
        if ignore_users is not None and isinstance(ignore_users, list):
            users = filter(lambda _user: _user.username not in ignore_users, users)

        for _user in users:
            text = 'I am {}'.format(_user.username)
            tweet = models.Tweet()
            tweet.user = _user
            tweet.text = text
            tweet.save()

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

    def test_valid_no_other_users_tweet(self):
        self.create_tweets([self.owner.username])

        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        _tweets = response.context.get('tweets')
        self.assertEqual(_tweets.count(), 0)

    def test_valid_follower_tweet(self):
        self.create_tweets([self.owner.username])
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
        self.create_tweets()
        follower = self.users[-1]
        relationship = models.Relationship()
        relationship.owner = self.owner
        relationship.follower = follower
        relationship.save()

        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        _tweets = response.context.get('tweets')
        self.assertEqual(_tweets.count(), 2)

class DeleteTweetViewTests(SNSView):
    @override_settings(AXES_ENABLED=False)
    def setUp(self):
        super().setUp()
        self.client.login(username=self.owner.username, password=self.password)

    def test_resolve_url(self):
        resolver = resolve('/sns/delete_tweet/{}'.format(1))
        self.chk_class(resolver, views.DeleteTweetView)

    def __create_own_tweets(self, num_tweet=3):
        for idx in range(num_tweet):
            text = '[Count{}] I am {}.'.format(idx, self.owner.username)
            tweet = models.Tweet()
            tweet.user = self.owner
            tweet.text = text
            tweet.save()

    def test_valid_get_request(self):
        self.__create_own_tweets()
        tweet = models.Tweet.objects.first()
        params = {
            'pk': tweet.pk,
        }
        url = reverse('sns:tweet_delete', kwargs=params)
        response = self.client.get(url)
        self.assertEqual(response.status_code, 403)

    def test_valid_post_request(self):
        self.__create_own_tweets()
        tweet = models.Tweet.objects.first()
        params = {
            'pk': tweet.pk,
        }
        url = reverse('sns:tweet_delete', kwargs=params)
        response = self.client.post(url, follow=True)
        self.assertEqual(response.status_code, 200)
        with self.assertRaises(models.Tweet.DoesNotExist):
            _ = models.Tweet.objects.get(pk=tweet.pk)

    def test_invalid_not_exist_tweet(self):
        self.__create_own_tweets()
        params = {
            'pk': models.Tweet.objects.count() + 1,
        }
        url = reverse('sns:tweet_delete', kwargs=params)
        response = self.client.post(url)
        self.assertEqual(response.status_code, 404)

    def test_invalid_no_login(self):
        self.__create_own_tweets()
        tweet = models.Tweet.objects.first()
        params = {
            'pk': tweet.pk,
        }
        self.client.logout()
        url = reverse('sns:tweet_delete', kwargs=params)
        response = self.client.post(url)
        self.assertEqual(response.status_code, 403)
        _ = models.Tweet.objects.get(pk=tweet.pk)

    def test_invalid_delete_other_users_tweet(self):
        self.create_tweets([self.owner.username])
        tweet = models.Tweet.objects.first()
        params = {
            'pk': tweet.pk,
        }
        url = reverse('sns:tweet_delete', kwargs=params)
        response = self.client.post(url)
        self.assertEqual(response.status_code, 403)
        _ = models.Tweet.objects.get(pk=tweet.pk)

class SearchFollowerViewTests(SNSView):
    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        follower0, follower1, follower2, follower3, follower4 = cls.owner, *cls.candidate_followers[:4]

        relationships = [
            (follower0, follower1),
            (follower0, follower4),
            (follower1, follower0),
            (follower2, follower1),
            (follower2, follower3),
            (follower2, follower4),
            (follower4, follower3),
        ]
        for _owner, _follower in relationships:
            _relationship = models.Relationship()
            _relationship.owner = _owner
            _relationship.follower = _follower
            _relationship.save()

        cls.url = reverse('sns:search_follower')

    def test_resolve_url(self):
        resolver = resolve('/sns/follower/search')
        self.chk_class(resolver, views.SearchFollowerView)

    @override_settings(AXES_ENABLED=False)
    def test_valid_get_request(self):
        self.client.login(username=self.owner.username, password=self.password)
        response = self.client.get(self.url)
        context_keys = response.context.keys()
        self.assertEqual(response.status_code, 200)
        self.assertTrue('relationship_form' in context_keys)
        self.assertTrue('relationships' in context_keys)
        self.assertTrue('filter' in context_keys)
        relationships = response.context['relationships']
        filter_info = response.context['filter']
        self.assertEqual(relationships.count(), 2)
        self.assertEqual(filter_info.qs().count(), UserModel.objects.count())

    @override_settings(AXES_ENABLED=False)
    def test_valid_no_follower(self):
        follower3 = self.candidate_followers[2]
        self.client.login(username=follower3.username, password=self.password)
        response = self.client.get(self.url)
        context_keys = response.context.keys()
        self.assertEqual(response.status_code, 200)
        self.assertTrue('relationships' in context_keys)
        relationships = response.context['relationships']
        self.assertEqual(relationships.count(), 0)

class CreateRelationshipViewTests(SNSView):
    @override_settings(AXES_ENABLED=False)
    def setUp(self):
        super().setUp()
        self.client.login(username=self.owner.username, password=self.password)
        self.url = reverse('sns:create_follower')
        self.redirect_url = reverse('sns:search_follower')

    def test_resolve_url(self):
        resolver = resolve('/sns/follower/create')
        self.chk_class(resolver, views.CreateRelationshipView)

    def test_valid_get_request(self):
        response = self.client.get(self.url)
        self.assertRedirects(response, self.redirect_url, status_code=302, target_status_code=200, msg_prefix='', fetch_redirect_response=True)

    def test_valid_post_request(self):
        follower = self.candidate_followers[0]

        data = {
            'owner_id': self.owner.pk,
            'follower_id': follower.pk,
        }
        response = self.client.post(self.url, data)
        self.assertRedirects(response, self.redirect_url, status_code=302, target_status_code=200, msg_prefix='', fetch_redirect_response=True)
        relationships = models.Relationship.objects.all()
        _relationship = relationships.first()
        self.assertEqual(relationships.count(), 1)
        self.assertEqual(_relationship.owner, self.owner)
        self.assertEqual(_relationship.follower, follower)

    def test_invalid_owner_is_not_request_user(self):
        follower = self.candidate_followers[0]

        data = {
            'owner_id': follower.pk,
            'follower_id': follower.pk,
        }
        response = self.client.post(self.url, data)
        self.assertRedirects(response, self.redirect_url, status_code=302, target_status_code=200, msg_prefix='', fetch_redirect_response=True)
        relationships = models.Relationship.objects.all()
        self.assertEqual(relationships.count(), 0)

    def test_invalid_follower_is_request_user(self):
        data = {
            'owner_id': self.owner.pk,
            'follower_id': self.owner.pk,
        }
        response = self.client.post(self.url, data)
        self.assertRedirects(response, self.redirect_url, status_code=302, target_status_code=200, msg_prefix='', fetch_redirect_response=True)
        relationships = models.Relationship.objects.all()
        self.assertEqual(relationships.count(), 0)

    def test_invalid_data_reverse_order(self):
        follower = self.candidate_followers[0]

        data = {
            'owner_id': follower.pk,
            'follower_id': self.owner.pk,
        }
        response = self.client.post(self.url, data)
        self.assertRedirects(response, self.redirect_url, status_code=302, target_status_code=200, msg_prefix='', fetch_redirect_response=True)
        relationships = models.Relationship.objects.all()
        self.assertEqual(relationships.count(), 0)

class DeleteRelationshipViewTests(SNSView):
    @override_settings(AXES_ENABLED=False)
    def setUp(self):
        super().setUp()
        self.client.login(username=self.owner.username, password=self.password)
        follower0, follower1, follower2, follower3, follower4 = self.owner, *self.candidate_followers[:4]

        relationships = [
            (follower0, follower1),
            (follower0, follower4),
            (follower1, follower0),
            (follower2, follower1),
            (follower2, follower3),
            (follower2, follower4),
            (follower4, follower3),
        ]
        for _owner, _follower in relationships:
            _relationship = models.Relationship()
            _relationship.owner = _owner
            _relationship.follower = _follower
            _relationship.save()

        self.relationships = models.Relationship.objects.all()

    def test_resolve_url(self):
        resolver = resolve('/sns/follower/delete/1')
        self.chk_class(resolver, views.DeleteRelationshipView)

    def test_valid_get_request(self):
        _relationship = self.relationships.filter(owner=self.owner).first()
        params = {
            'pk': _relationship.pk,
        }
        url = reverse('sns:delete_follower', kwargs=params)
        response = self.client.get(url)
        self.assertEqual(response.status_code, 403)
        _ = models.Relationship.objects.get(pk=_relationship.pk)

    def test_valid_post_request(self):
        _relationship = self.relationships.filter(owner=self.owner).first()
        params = {
            'pk': _relationship.pk,
        }
        url = reverse('sns:delete_follower', kwargs=params)
        response = self.client.post(url, follow=True)
        self.assertEqual(response.status_code, 200)
        with self.assertRaises(models.Relationship.DoesNotExist):
            _ = models.Relationship.objects.get(pk=_relationship.pk)

    def test_invalid_delete_other_owners_record(self):
        _relationship = self.relationships.exclude(owner=self.owner).first()
        params = {
            'pk': _relationship.pk,
        }
        url = reverse('sns:delete_follower', kwargs=params)
        response = self.client.post(url, follow=True)
        self.assertEqual(response.status_code, 403)
        _ = models.Relationship.objects.get(pk=_relationship.pk)

    def test_invalid_does_not_exist_relationship(self):
        params = {
            'pk': self.relationships.count() + 1,
        }
        url = reverse('sns:delete_follower', kwargs=params)
        response = self.client.post(url, follow=True)
        self.assertEqual(response.status_code, 404)

    def test_invalid_no_login(self):
        _relationship = self.relationships.filter(owner=self.owner).first()
        params = {
            'pk': _relationship.pk,
        }
        self.client.logout()
        url = reverse('sns:delete_follower', kwargs=params)
        response = self.client.post(url, follow=True)
        self.assertEqual(response.status_code, 403)
        _ = models.Relationship.objects.get(pk=_relationship.pk)
