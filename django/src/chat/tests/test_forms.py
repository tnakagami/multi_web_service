from unittest import mock
from django.test import TestCase
from registration.tests.factories import UserFactory, UserModel
from chat.tests.factories import RoomFactory, MessageFactory
from chat import models, forms

class ChatForm(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

    @classmethod
    def setUpTestData(cls):
        cls.users = UserFactory.create_batch(5)
        cls.not_active_user = UserFactory(username='not_active', is_active=False)
        u_pk = [_user.pk for _user in cls.users]
        cls.rooms = [
            (RoomFactory.create(owner=cls.users[0]), RoomFactory.create(owner=cls.users[0], name='sample_a', assigned=[u_pk[1], u_pk[2]]), ),          # invalid: user[3], user[4]
            (RoomFactory.create(owner=cls.users[1]), RoomFactory.create(owner=cls.users[1], name='sample_b', assigned=[u_pk[0], u_pk[2], u_pk[4]]), ), # invalid: user[3]
            (RoomFactory.create(owner=cls.users[2]), RoomFactory.create(owner=cls.users[2], name='sample_c', assigned=[u_pk[3]]), ),          # invalid: user[0], user[1], user[4]
            (RoomFactory.create(owner=cls.users[3], name='only_user3'), RoomFactory.create(owner=cls.users[3], name='only_c'), ),             # invalid: 0, 1, 2, 4
        ]
        _room = cls.rooms[0][-1]
        messages = [
            (cls.users[0], 'chat'), (cls.users[0], 'sample'), (cls.users[0], 'hello'), (cls.users[0], 'world'), (cls.users[0], 'hello world'), (cls.users[0], 'user0'),
                                    (cls.users[1], 'sample'),                                                   (cls.users[1], 'hello world'), (cls.users[1], 'user1'),
        ]
        cls.messages = [MessageFactory(user=_user, room=_room, content=_msg) for _user, _msg in messages]

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()

class RoomSearchFormTests(ChatForm):
    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        cls.model = models.Room
        cls.form = forms.RoomSearchForm

    def test_form(self):
        search_word = 'abc'
        data = {
            'search_word': search_word,
        }
        form = self.form(data)
        self.assertTrue(form.is_valid())

    def test_chk_returned_queryset_for_search_word_pattern1(self):
        search_word = 'sample'
        data = {
            'search_word': search_word,
        }
        form = self.form(data)
        self.assertTrue(form.is_valid())
        form.clean()
        _queryset = form.filtered_queryset(self.model.objects.all())
        self.assertEqual(_queryset.count(), 3)
        self.assertEqual(_queryset.filter(owner=self.users[0]).count(), 1)
        self.assertEqual(_queryset.filter(owner=self.users[1]).count(), 1)
        self.assertEqual(_queryset.filter(owner=self.users[2]).count(), 1)
        self.assertEqual(_queryset.filter(owner=self.users[3]).count(), 0)
        self.assertEqual(_queryset.filter(owner=self.users[4]).count(), 0)

    def test_chk_returned_queryset_for_search_word_pattern2(self):
        search_word = 'only'
        data = {
            'search_word': search_word,
        }
        form = self.form(data)
        self.assertTrue(form.is_valid())
        form.clean()
        _queryset = form.filtered_queryset(self.model.objects.all())
        self.assertEqual(_queryset.count(), 2)
        self.assertEqual(_queryset.filter(owner=self.users[0]).count(), 0)
        self.assertEqual(_queryset.filter(owner=self.users[1]).count(), 0)
        self.assertEqual(_queryset.filter(owner=self.users[2]).count(), 0)
        self.assertEqual(_queryset.filter(owner=self.users[3]).count(), 2)
        self.assertEqual(_queryset.filter(owner=self.users[4]).count(), 0)

    def test_chk_returned_queryset_for_search_word_pattern3(self):
        search_word = 'sample_b'
        data = {
            'search_word': search_word,
        }
        form = self.form(data)
        self.assertTrue(form.is_valid())
        form.clean()
        _queryset = form.filtered_queryset(self.model.objects.all())
        self.assertEqual(_queryset.count(), 1)
        # check owner
        self.assertEqual(_queryset.filter(owner=self.users[0]).count(), 0)
        self.assertEqual(_queryset.filter(owner=self.users[1]).count(), 1)
        self.assertEqual(_queryset.filter(owner=self.users[2]).count(), 0)
        self.assertEqual(_queryset.filter(owner=self.users[3]).count(), 0)
        self.assertEqual(_queryset.filter(owner=self.users[4]).count(), 0)
        # check assignment
        _room = _queryset.first()
        self.assertTrue(_room.is_assigned(self.users[0]))
        self.assertTrue(_room.is_assigned(self.users[1]))
        self.assertTrue(_room.is_assigned(self.users[2]))
        self.assertFalse(_room.is_assigned(self.users[3]))
        self.assertTrue(_room.is_assigned(self.users[4]))

class RoomFormTests(ChatForm):
    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        cls.superuser = UserFactory(username='superuser', is_staff=True, is_superuser=True)
        cls.staffuser = UserFactory(username='staffuser', is_staff=True, is_superuser=False)
        cls.model = models.Room
        cls.form = forms.RoomForm
        cls.targets = ('name', 'description', 'assigned')

    def test_form(self):
        data = {key: '{}1'.format(key) for key in self.targets}
        data['assigned'] = 0
        form = self.form(data)
        self.assertTrue(form.is_valid())

    def test_chk_invalid_data(self):
        data = {key: '{}1'.format(key) for key in self.targets}
        data['assigned'] = 0

        for key in self.targets:
            tmp_data = {_key: data[_key] for _key in self.targets}

            if key in ['assigned']:
                tmp_data[key] = '{}1'.format(key)
            else:
                tmp_data[key] = ''

            form = self.form(tmp_data)
            self.assertFalse(form.is_valid())

    def test_chk_specific_user(self):
        data = {}
        form = self.form(data, user=self.users[3])
        self.assertEqual(form.fields['assigned'].queryset.count(), 4)
        _queryset = form.fields['assigned'].queryset

        for idx in [0, 1, 2, 4]:
            _ = _queryset.get(pk=self.users[idx].pk)

        with self.assertRaises(UserModel.DoesNotExist):
            _ = _queryset.get(pk=self.not_active_user.pk)

class MessageSearchFormTests(ChatForm):
    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        cls.model = models.Message
        cls.form = forms.MessageSearchForm

    def test_form(self):
        search_word = 'abc'
        data = {
            'search_word': search_word,
        }
        form = self.form(data)
        self.assertTrue(form.is_valid())

    def test_chk_returned_queryset_for_search_word_pattern1(self):
        search_word = 'sample'
        data = {
            'search_word': search_word,
        }
        form = self.form(data)
        self.assertTrue(form.is_valid())
        form.clean()
        _queryset = form.filtered_queryset(self.model.objects.all())
        self.assertEqual(_queryset.count(), 2)
        self.assertEqual(_queryset.filter(user=self.users[0]).count(), 1)
        self.assertEqual(_queryset.filter(user=self.users[1]).count(), 1)
        self.assertEqual(_queryset.filter(user=self.users[2]).count(), 0)
        self.assertEqual(_queryset.filter(user=self.users[3]).count(), 0)
        self.assertEqual(_queryset.filter(user=self.users[4]).count(), 0)

    def test_chk_returned_queryset_for_search_word_pattern2(self):
        search_word = 'hello'
        data = {
            'search_word': search_word,
        }
        form = self.form(data)
        self.assertTrue(form.is_valid())
        form.clean()
        _queryset = form.filtered_queryset(self.model.objects.all())
        self.assertEqual(_queryset.count(), 3)
        self.assertEqual(_queryset.filter(user=self.users[0]).count(), 2)
        self.assertEqual(_queryset.filter(user=self.users[1]).count(), 1)
        self.assertEqual(_queryset.filter(user=self.users[2]).count(), 0)
        self.assertEqual(_queryset.filter(user=self.users[3]).count(), 0)
        self.assertEqual(_queryset.filter(user=self.users[4]).count(), 0)

    def test_chk_returned_queryset_for_search_word_pattern3(self):
        search_word = 'not_exist'
        data = {
            'search_word': search_word,
        }
        form = self.form(data)
        self.assertTrue(form.is_valid())
        form.clean()
        _queryset = form.filtered_queryset(self.model.objects.all())
        self.assertEqual(_queryset.count(), 0)
