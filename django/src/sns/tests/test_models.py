from django.test import TestCase
from registration.tests.factories import UserFactory
from sns import models

class SNSModel(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        cls.users = UserFactory.create_batch(10)

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()

class TweetTests(SNSModel):
    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        cls.model = models.Tweet

    def __create_and_save(self, user, text=None):
        tweet = self.model()
        tweet.user = user
        if tweet is not None:
            tweet.text = text
        tweet.save()

        return tweet

    def __chk_instance_data(self, pk, user, text):
        tweet = self.model.objects.get(pk=pk)
        self.assertEqual(tweet.user, user)
        self.assertEqual(tweet.text, text)

    def test_tweet_is_empty(self):
        self.assertEqual(self.model.objects.count(), 0)

    def test_create_tweet(self):
        tweet_message = 'abc'
        _user = self.users[0]
        _tweet = self.__create_and_save(_user, tweet_message)
        self.__chk_instance_data(_tweet.pk, _user, tweet_message)
        self.assertEqual(self.model.objects.count(), 1)
        self.assertEqual(str(_tweet), tweet_message)

class RelationshipTests(SNSModel):
    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        cls.model = models.Relationship

    def __create_and_save(self, owner, follower):
        relationship = self.model()
        relationship.owner = owner
        relationship.follower = follower
        relationship.save()

        return relationship

    def __chk_instance_data(self, pk, owner, follower):
        relationship = self.model.objects.get(pk=pk)
        self.assertEqual(relationship.owner, owner)
        self.assertEqual(relationship.follower, follower)

    def test_relationship_is_empty(self):
        self.assertEqual(self.model.objects.count(), 0)

    def test_create_relationship(self):
        _owner, _follower = self.users[:2]
        _relationship = self.__create_and_save(_owner, _follower)
        self.__chk_instance_data(_relationship.pk, _owner, _follower)
        self.assertEqual(self.model.objects.count(), 1)
        self.assertEqual(str(_relationship), '{}-{}'.format(_owner.username, _follower.username))

    def test_multi_user_relationship(self):
        _owner, _follower1, _follower2 = self.users[:3]
        _relationship =self.__create_and_save(_owner, _follower1)
        self.__chk_instance_data(_relationship.pk, _owner, _follower1)
        _relationship = self.__create_and_save(_owner, _follower2)
        self.__chk_instance_data(_relationship.pk, _owner, _follower2)
        self.assertEqual(self.model.objects.count(), 2)
        self.assertEqual(self.model.objects.filter(owner__username=_owner.username).count(), 2)

    def test_follow_for_follow(self):
        _owner, _follower1, _follower2 = self.users[:3]

        dataset = [
            (_owner, _follower1),
            (_follower1, _owner),
            (_follower1, _follower2),
            (_owner, _follower2),
        ]

        for c_owner, c_follower in dataset:
            _relationship =self.__create_and_save(c_owner, c_follower)
            self.__chk_instance_data(_relationship.pk, c_owner, c_follower)

        # owner
        expected_owners = [
            (_owner, 2),
            (_follower1, 2),
            (_follower2, 0),
        ]
        expected_followers = [
            (_owner, 1),
            (_follower1, 1),
            (_follower2, 2),
        ]
        for _user, _count in expected_owners:
            self.assertEqual(self.model.objects.filter(owner__username=_user.username).count(), _count)
        for _user, _count in expected_followers:
            self.assertEqual(self.model.objects.filter(follower__username=_user.username).count(), _count)
