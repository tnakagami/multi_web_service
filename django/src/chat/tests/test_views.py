from unittest import mock
from django.test import TestCase
from django.test.utils import override_settings
from django.urls import reverse, resolve
from registration.tests.factories import UserFactory, UserModel
from chat.tests.factories import RoomFactory, MessageFactory
from chat import views, models

class ChatView(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

    @classmethod
    def setUpTestData(cls):
        cls.password = 'password'
        cls.users = UserFactory.create_batch(5)
        u_pk = [_user.pk for _user in cls.users]
        cls.rooms = [
            (RoomFactory.create(owner=cls.users[0]), RoomFactory.create(owner=cls.users[0], name='sample_a', assigned=[u_pk[1], u_pk[2]]), ),          # invalid: user[3], user[4]
            (RoomFactory.create(owner=cls.users[1]), RoomFactory.create(owner=cls.users[1], name='sample_b', assigned=[u_pk[0], u_pk[2], u_pk[4]]), ), # invalid: user[3]
            (RoomFactory.create(owner=cls.users[2]), RoomFactory.create(owner=cls.users[2], name='sample_c', assigned=[u_pk[3]]), ),          # invalid: user[0], user[1], user[4]
            (RoomFactory.create(owner=cls.users[3], name='only_user3'), RoomFactory.create(owner=cls.users[3], name='only_c'), ),             # invalid: 0, 1, 2, 4
            (RoomFactory.create(owner=cls.users[3], name='only_user3_part2'), RoomFactory.create(owner=cls.users[3], name='only_c2'), ),      # invalid: 0, 1, 2, 4
            (RoomFactory.create(owner=cls.users[3], name='only_user3_part3'), RoomFactory.create(owner=cls.users[3], name='only_c3'), ),      # invalid: 0, 1, 2, 4
            (RoomFactory.create(owner=cls.users[3], name='only_user3_part4'), RoomFactory.create(owner=cls.users[3], name='only_c4'), ),      # invalid: 0, 1, 2, 4
        ]

    def chk_class(self, resolver, class_view):
        self.assertEqual(resolver.func.__name__, class_view.__name__)

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()

class RoomListViewTests(ChatView):
    @override_settings(AXES_ENABLED=False)
    def setUp(self):
        super().setUp()
        self.client.login(username=self.users[0].username, password=self.password)
        self.url = reverse('chat:index')

    def test_resolve_url(self):
        resolver = resolve('/chat/')
        self.chk_class(resolver, views.RoomListView)

    def test_no_login_access(self):
        self.client.logout()
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 302)

    def test_listed_rooms(self):
        response = self.client.get(self.url)
        self.assertTemplateUsed('chat/index.html')
        self.assertEqual(response.status_code, 200)
        self.assertTrue('rooms' in response.context.keys())
        self.assertTrue('paginator' in response.context.keys())
        _rooms = response.context.get('rooms')
        _paginator = response.context.get('paginator')
        self.assertEqual(_rooms.count(), 10)
        self.assertEqual(_paginator.page_range[-1], 2)

    def test_chk_pagination(self):
        data = {
            'page': 2,
        }
        response = self.client.get(self.url, data)
        self.assertEqual(response.status_code, 200)
        self.assertTrue('rooms' in response.context.keys())
        _rooms = response.context.get('rooms')
        self.assertEqual(_rooms.count(), 4) # 14 % 10: total_rooms_count % paginate_by

    @override_settings(AXES_ENABLED=False)
    def test_no_rooms(self):
        user = self.users[-1]
        self.client.logout()
        self.client.login(username=user.username, password=self.password)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        _rooms = response.context.get('rooms')
        self.assertEqual(len([room for room in _rooms if room.owner == user]), 0)

    def test_filtered_posts(self):
        data = {
            'search_word': 'sample',
        }
        response = self.client.get(self.url, data)
        self.assertEqual(response.status_code, 200)
        _rooms = response.context.get('rooms')
        self.assertEqual(_rooms.count(), 3)
