from unittest import mock
from django.test import TestCase, RequestFactory
from django.test.utils import override_settings
from django.urls import reverse, resolve
from registration.tests.factories import UserFactory
from chat.tests.factories import RoomFactory, MessageFactory
from chat import views, models

class ChatView(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

    @classmethod
    def setUpTestData(cls):
        cls.password = 'password'
        cls.superuser = UserFactory(username='superuser', is_staff=True, is_superuser=True)
        cls.staffuser = UserFactory(username='staffuser', is_staff=True, is_superuser=False)
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

class PaginateTests(ChatView):
    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        cls.factory = RequestFactory()
        _room = cls.rooms[0][0]
        _user = cls.users[0]
        MessageFactory.create_batch(17, user=_user, room=_room)
        cls.count = 5
        cls.queryset = models.Message.objects.all().order_by('-created_at')

    def test_get_query_pattern1(self):
        request = self.factory.get('/', {'page': 3})
        _, page_obj = views.paginate_query(request, self.queryset, self.count)
        self.assertEqual(len(page_obj), 5)
        self.assertEqual(page_obj.number, 3)

    def test_get_query_pattern2(self):
        request = self.factory.get('/', {'page': 4})
        _, page_obj = views.paginate_query(request, self.queryset, self.count)
        self.assertEqual(len(page_obj), 2)
        self.assertEqual(page_obj.number, 4)

    def test_is_not_integer(self):
        request = self.factory.get('/', {'page': 'a'})
        _, page_obj = views.paginate_query(request, self.queryset, self.count)
        self.assertEqual(len(page_obj), 5)
        self.assertEqual(page_obj.number, 1)

    def test_is_empty(self):
        request = self.factory.get('/', {'page': -1})
        _, page_obj= views.paginate_query(request, self.queryset, self.count)
        self.assertEqual(len(page_obj), 2)
        self.assertEqual(page_obj.number, 4)

class RoomListViewTests(ChatView):
    @override_settings(AXES_ENABLED=False)
    def setUp(self):
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

class RoomCreateViewTests(ChatView):
    @override_settings(AXES_ENABLED=False)
    def setUp(self):
        self.client.login(username=self.users[0].username, password=self.password)
        self.url = reverse('chat:room_create')

    def test_resolve_url(self):
        resolver = resolve('/chat/room/create')
        self.chk_class(resolver, views.RoomCreateView)

    def test_no_login_access(self):
        self.client.logout()
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 403)

    def test_chk_room_form(self):
        response = self.client.get(self.url)
        self.assertTemplateUsed('chat/room_form.html')
        self.assertEqual(response.status_code, 200)
        self.assertTrue('form' in response.context.keys())
        _form = response.context.get('form')
        self.assertTrue('assigned' in _form.fields.keys())
        _assigned_qs = _form.fields['assigned'].queryset
        self.assertEqual(_assigned_qs.count(), 4)
        expected = [self.users[idx].pk for idx in [1,2,3,4]]
        for _user in _assigned_qs:
            self.assertTrue(_user.pk in expected)

    def test_creating_room(self):
        data = {
            'name': 'chat_room_created',
            'description': 'sample_chat_created',
            'assigned': [self.users[1].pk, self.users[3].pk],
        }
        response = self.client.post(self.url, data, follow=True)
        self.assertEqual(response.status_code, 200)
        _room = models.Room.objects.all().last()
        _assigned = list(_room.assigned.all().values_list('pk', flat=True))
        self.assertEqual(_room.owner, self.users[0])
        self.assertEqual(_room.name, data['name'])
        self.assertEqual(_room.description, data['description'])
        self.assertEquals(_assigned, data['assigned'])

class RoomUpdateViewTests(ChatView):
    @override_settings(AXES_ENABLED=False)
    def setUp(self):
        self.client.login(username=self.users[0].username, password=self.password)
        self.assigned = [self.users[1].pk, self.users[3].pk]
        self.created_room = RoomFactory.create(owner=self.users[0], assigned=self.assigned)

    def test_resolve_url(self):
        resolver = resolve('/chat/room/update/123')
        self.chk_class(resolver, views.RoomUpdateView)

    def test_no_login_access(self):
        self.client.logout()
        data = {
            'pk': self.created_room.pk,
        }
        url = reverse('chat:room_update', kwargs=data)
        response = self.client.get(url)
        self.assertEqual(response.status_code, 403)

    def test_updating_room(self):
        data = {
            'pk': self.created_room.pk,
        }
        url = reverse('chat:room_update', kwargs=data)
        updated_assigned = [self.users[2].pk]
        data = {
            'name': 'updated_name',
            'description': 'updated_description',
            'assigned': updated_assigned,
        }
        response = self.client.post(url, data, follow=True)
        self.assertTemplateUsed('chat/room_form.html')
        self.assertEqual(response.status_code, 200)
        _room = models.Room.objects.get(pk=self.created_room.pk)
        self.assertEqual(_room.owner, self.users[0])
        self.assertEqual(_room.name, data['name'])
        self.assertEqual(_room.description, data['description'])
        self.assertEqual(_room.assigned.all().count(), 1)
        self.assertEquals(list(_room.assigned.all().values_list('pk', flat=True)), updated_assigned)

    def test_not_exist_room(self):
        data = {
            'pk': models.Room.objects.count() + 1,
        }
        url = reverse('chat:room_update', kwargs=data)
        response = self.client.post(url, follow=True)
        self.assertEqual(response.status_code, 404)
        _room = models.Room.objects.get(pk=self.created_room.pk)
        self.assertEqual(_room.owner, self.created_room.owner)
        self.assertEqual(_room.name, self.created_room.name)
        self.assertEqual(_room.description, self.created_room.description)
        self.assertEquals(_room.assigned.all().count(), self.created_room.assigned.all().count())
        self.assertEquals(list(_room.assigned.all().values_list('pk', flat=True)), list(self.created_room.assigned.all().values_list('pk', flat=True)))

    def test_room_defined_by_other_user(self):
        target_room = self.rooms[-1][0]
        data = {
            'pk': target_room.pk,
        }
        url = reverse('chat:room_update', kwargs=data)
        response = self.client.post(url, follow=True)
        self.assertEqual(response.status_code, 403)
        _room = models.Room.objects.get(pk=target_room.pk)
        self.assertEqual(_room.owner, target_room.owner)
        self.assertEqual(_room.name, target_room.name)
        self.assertEqual(_room.description, target_room.description)
        self.assertEquals(_room.assigned.all().count(), target_room.assigned.all().count())
        self.assertEquals(list(_room.assigned.all().values_list('pk', flat=True)), list(target_room.assigned.all().values_list('pk', flat=True)))

class RoomDeleteViewTests(ChatView):
    @override_settings(AXES_ENABLED=False)
    def setUp(self):
        self.client.login(username=self.users[0].username, password=self.password)
        self.assigned = [self.users[1].pk, self.users[3].pk]
        self.target_room = RoomFactory.create(owner=self.users[0], assigned=self.assigned)

    def test_resolve_url(self):
        resolver = resolve('/chat/room/delete/123')
        self.chk_class(resolver, views.RoomDeleteView)

    def test_no_login_access(self):
        self.client.logout()
        data = {
            'pk': self.target_room.pk,
        }
        url = reverse('chat:room_delete', kwargs=data)
        response = self.client.post(url)
        self.assertEqual(response.status_code, 403)

    def test_get_access(self):
        data = {
            'pk': self.target_room.pk,
        }
        url = reverse('chat:room_delete', kwargs=data)
        response = self.client.get(url)
        self.assertEqual(response.status_code, 403)

    def test_deleting_target_room(self):
        data = {
            'pk': self.target_room.pk,
        }
        url = reverse('chat:room_delete', kwargs=data)
        response = self.client.post(url, follow=True)
        self.assertEqual(response.status_code, 200)
        with self.assertRaises(models.Room.DoesNotExist):
            _ = models.Room.objects.get(pk=self.target_room.pk)

    def test_not_exist_room(self):
        data = {
            'pk': models.Room.objects.count() + 1,
        }
        url = reverse('chat:room_delete', kwargs=data)
        response = self.client.post(url, follow=True)
        self.assertEqual(response.status_code, 404)
        _ = models.Room.objects.get(pk=self.target_room.pk)

    def test_room_defined_by_other_user(self):
        target_room = self.rooms[-1][0]
        data = {
            'pk': target_room.pk,
        }
        url = reverse('chat:room_delete', kwargs=data)
        response = self.client.post(url, follow=True)
        self.assertEqual(response.status_code, 403)
        _ = models.Room.objects.get(pk=target_room.pk)

class ChatRoomDetailViewTests(ChatView):
    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        _room = cls.rooms[0][-1]
        data = {
            'pk': _room.pk,
        }
        cls.url = reverse('chat:chat_room', kwargs=data)
        messages = [
            (cls.users[0], 'chat'), (cls.users[0], 'sample'), (cls.users[0], 'hello'), (cls.users[0], 'world'), (cls.users[0], 'hello world'), (cls.users[0], 'user0'),
                                    (cls.users[1], 'sample'),                                                   (cls.users[1], 'hello world'), (cls.users[1], 'user1'),
        ]
        cls.messages = [MessageFactory(user=_user, room=_room, content=_msg) for _user, _msg in messages]

    @override_settings(AXES_ENABLED=False)
    def setUp(self):
        self.client.login(username=self.users[0].username, password=self.password)

    def test_resolve_url(self):
        resolver = resolve('/chat/room/123')
        self.chk_class(resolver, views.ChatRoomDetailView)

    def test_no_login_access(self):
        self.client.logout()
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 403)

    def test_access_owner_user0(self):
        response = self.client.get(self.url)
        self.assertTemplateUsed('chat/chat_room.html')
        self.assertEqual(response.status_code, 200)

    @override_settings(AXES_ENABLED=False)
    def test_access_is_assigned_user1(self):
        self.client.logout()
        self.client.login(username=self.users[1].username, password=self.password)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)

    @override_settings(AXES_ENABLED=False)
    def test_access_is_assigned_user2(self):
        self.client.logout()
        self.client.login(username=self.users[2].username, password=self.password)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)

    @override_settings(AXES_ENABLED=False)
    def test_access_is_not_assigned_user3(self):
        self.client.logout()
        self.client.login(username=self.users[3].username, password=self.password)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 403)

    @override_settings(AXES_ENABLED=False)
    def test_access_is_not_assigned_user4(self):
        self.client.logout()
        self.client.login(username=self.users[4].username, password=self.password)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 403)

    def test_access_other_room_is_assigned(self):
        data = {
            'pk': self.rooms[1][-1].pk,
        }
        url = reverse('chat:chat_room', kwargs=data)
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_access_other_room_is_not_assigned(self):
        data = {
            'pk': self.rooms[2][-1].pk,
        }
        url = reverse('chat:chat_room', kwargs=data)
        response = self.client.get(url)
        self.assertEqual(response.status_code, 403)

    def test_not_exist_room(self):
        data = {
            'pk': models.Room.objects.count() + 1,
        }
        url = reverse('chat:chat_room', kwargs=data)
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)

    def test_search_message_pattern1(self):
        data = {
            'search_word': 'sample',
        }
        response = self.client.get(self.url, data)
        self.assertEqual(response.status_code, 200)
        self.assertTrue('page_obj' in response.context.keys())
        _page_obj = response.context['page_obj']
        self.assertEqual(len(_page_obj), 2)
        user0_messages = [msg for msg in _page_obj if msg.user.pk == self.users[0].pk]
        user1_messages = [msg for msg in _page_obj if msg.user.pk == self.users[1].pk]
        self.assertEqual(len(user0_messages), 1)
        self.assertEqual(len(user1_messages), 1)

    def test_search_message_pattern2(self):
        data = {
            'search_word': 'hello',
        }
        response = self.client.get(self.url, data)
        self.assertEqual(response.status_code, 200)
        self.assertTrue('page_obj' in response.context.keys())
        _page_obj = response.context['page_obj']
        self.assertEqual(len(_page_obj), 3)
        user0_messages = [msg for msg in _page_obj if msg.user.pk == self.users[0].pk]
        user1_messages = [msg for msg in _page_obj if msg.user.pk == self.users[1].pk]
        self.assertEqual(len(user0_messages), 2)
        self.assertEqual(len(user1_messages), 1)

    def test_search_message_pattern3(self):
        data = {
            'search_word': 'chat',
        }
        response = self.client.get(self.url, data)
        self.assertEqual(response.status_code, 200)
        self.assertTrue('page_obj' in response.context.keys())
        _page_obj = response.context['page_obj']
        self.assertEqual(len(_page_obj), 1)
        user0_messages = [msg for msg in _page_obj if msg.user.pk == self.users[0].pk]
        user1_messages = [msg for msg in _page_obj if msg.user.pk == self.users[1].pk]
        self.assertEqual(len(user0_messages), 1)
        self.assertEqual(len(user1_messages), 0)

    def test_search_message_pattern4(self):
        data = {
            'search_word': 'not_exist',
        }
        response = self.client.get(self.url, data)
        self.assertEqual(response.status_code, 200)
        self.assertTrue('page_obj' in response.context.keys())
        _page_obj = response.context['page_obj']
        self.assertEqual(len(_page_obj), 0)
