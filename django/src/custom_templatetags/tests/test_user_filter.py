from django.test import TestCase
from custom_templatetags import user_filter
from registration.tests.factories import UserFactory, UserModel
from sns.models import Relationship

class UserFilter(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

    @classmethod
    def setUpTestData(cls):
        UserFactory.reset_sequence(0)
        cls.users = UserFactory.create_batch(5)
        cls.all_users = UserModel.objects.all()

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()

class FilteredUsernameTests(UserFilter):
    def test_only_one_user(self):
        queryset = user_filter.filtered_username(self.all_users, 'user1')
        self.assertEqual(queryset.count(), 1)

    def test_not_exist_user(self):
        queryset = user_filter.filtered_username(self.all_users, 'user')
        self.assertEqual(queryset.count(), 0)

class FilteredViewnameTests(UserFilter):
    def test_only_one_user(self):
        queryset = user_filter.filtered_viewname(self.all_users, 'viewname1')
        self.assertEqual(queryset.count(), 1)

    def test_not_exist_user(self):
        queryset = user_filter.filtered_viewname(self.all_users, 'viewname')
        self.assertEqual(queryset.count(), 0)

class RelationshipFilter(UserFilter):
    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        cls.owner = cls.users[0]
        candidate_followers = list(filter(lambda _user: cls.owner.pk != _user.pk, cls.users))
        follower0, follower1, follower2, follower3, follower4 = cls.owner, *candidate_followers[:4]

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
            _relationship = Relationship()
            _relationship.owner = _owner
            _relationship.follower = _follower
            _relationship.save()

        cls.all_relationships = Relationship.objects.all()

class FilteredOwnerTests(RelationshipFilter):
    def test_filtering_user0(self):
        queryset = user_filter.filtered_owner(self.all_relationships, self.users[0].pk)
        self.assertEqual(queryset.count(), 2)
    def test_filtering_user1(self):
        queryset = user_filter.filtered_owner(self.all_relationships, self.users[1].pk)
        self.assertEqual(queryset.count(), 1)
    def test_filtering_user2(self):
        queryset = user_filter.filtered_owner(self.all_relationships, self.users[2].pk)
        self.assertEqual(queryset.count(), 3)
    def test_filtering_user3(self):
        queryset = user_filter.filtered_owner(self.all_relationships, self.users[3].pk)
        self.assertEqual(queryset.count(), 0)
    def test_filtering_user4(self):
        queryset = user_filter.filtered_owner(self.all_relationships, self.users[4].pk)
        self.assertEqual(queryset.count(), 1)

class FilteredFollowerTests(RelationshipFilter):
    def test_filtering_user0(self):
        queryset = user_filter.filtered_follower(self.all_relationships, self.users[0].pk)
        self.assertEqual(queryset.count(), 1)
    def test_filtering_user1(self):
        queryset = user_filter.filtered_follower(self.all_relationships, self.users[1].pk)
        self.assertEqual(queryset.count(), 2)
    def test_filtering_user2(self):
        queryset = user_filter.filtered_follower(self.all_relationships, self.users[2].pk)
        self.assertEqual(queryset.count(), 0)
    def test_filtering_user3(self):
        queryset = user_filter.filtered_follower(self.all_relationships, self.users[3].pk)
        self.assertEqual(queryset.count(), 2)
    def test_filtering_user4(self):
        queryset = user_filter.filtered_follower(self.all_relationships, self.users[4].pk)
        self.assertEqual(queryset.count(), 2)

class GetFirstElementTests(RelationshipFilter):
    def test_get_first_element(self):
        user = user_filter.get_first_element(self.all_users)
        self.assertEqual(user, self.users[0])
        relationship = user_filter.get_first_element(self.all_relationships)
        all_relationships = list(self.all_relationships)
        self.assertEqual(relationship, all_relationships[0])

    def test_empty_queryset(self):
        _ = user_filter.get_first_element(UserModel.objects.none())
        _ = user_filter.get_first_element(Relationship.objects.none())

class IgnoredUserpkTests(RelationshipFilter):
    def test_ignore_user0(self):
        target_pk = self.users[0].pk
        queryset = user_filter.ignored_userpk(self.all_users, target_pk)
        with self.assertRaises(UserModel.DoesNotExist):
            _ = queryset.get(pk=target_pk)

    def test_ignore_relationship(self):
        relationship = self.all_relationships.first()
        target_pk = relationship.pk
        queryset = user_filter.ignored_userpk(self.all_relationships, target_pk)
        with self.assertRaises(Relationship.DoesNotExist):
            _ = queryset.get(pk=target_pk)

    def test_empty_queryset(self):
        relationship = self.all_relationships.first()
        _ = user_filter.ignored_userpk(UserModel.objects.none(), self.users[0].pk)
        _ = user_filter.ignored_userpk(Relationship.objects.none(), relationship.pk)
