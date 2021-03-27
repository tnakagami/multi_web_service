from django.test import TestCase
from registration.tests.factories import UserFactory
from chat import models

class ChatModel(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        cls.users = UserFactory.create_batch(5)

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()

class RoomTests(ChatModel):
    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        cls.model = models.Room

    def __create_and_save(self, data):
        room = self.model()
        room.owner = data['owner']
        room.name = data['name']
        room.description = data['description']
        room.save()
        if 'assigned' in data.keys():
            room.assigned.set(data['assigned'])
        room.save()

        return room

    def __chk_instance_data(self, pk, data):
        room = self.model.objects.get(pk=pk)

        num_assigned = data.pop('assigned')

        for key, value in data.items():
            self.assertEqual(getattr(room, key), value)
        self.assertEqual(room.assigned.all().count(), num_assigned)
        self.assertEqual(str(room), data['name'])

    def test_room_is_empty(self):
        self.assertEqual(self.model.objects.count(), 0)

    def test_create_room(self):
        room_name = 'chat room'
        data = {
            'owner': self.users[0],
            'name': room_name,
            'description': 'sample space',
            'assigned': [self.users[1].pk, self.users[2].pk],
        }
        expected = {
            'owner': data['owner'],
            'name': data['name'],
            'description': data['description'],
            'assigned': len(data['assigned']),
        }
        _room = self.__create_and_save(data)
        self.__chk_instance_data(_room.pk, expected)
        self.assertEqual(self.model.objects.count(), 1)
        self.assertTrue(_room.is_assigned(self.users[0]))
        self.assertTrue(_room.is_assigned(self.users[1]))
        self.assertTrue(_room.is_assigned(self.users[2]))
        self.assertFalse(_room.is_assigned(self.users[3]))
        self.assertFalse(_room.is_assigned(self.users[4]))

    def test_create_room_no_assignment(self):
        room_name = 'chat room'
        data = {
            'owner': self.users[0],
            'name': room_name,
            'description': 'sample space',
        }
        expected = {
            'owner': data['owner'],
            'name': data['name'],
            'description': data['description'],
            'assigned': 0,
        }
        _room = self.__create_and_save(data)
        self.__chk_instance_data(_room.pk, expected)
        self.assertEqual(self.model.objects.count(), 1)
        self.assertTrue(_room.is_assigned(self.users[0]))
        self.assertFalse(_room.is_assigned(self.users[1]))
        self.assertFalse(_room.is_assigned(self.users[2]))
        self.assertFalse(_room.is_assigned(self.users[3]))
        self.assertFalse(_room.is_assigned(self.users[4]))

class MessageTests(ChatModel):
    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        cls.model = models.Message
        cls.room = models.Room(
            owner=cls.users[0],
            name='chat room',
            description='sample space',
        )
        cls.room.save()
        cls.room.assigned.set([cls.users[1].pk, cls.users[2].pk])

    def __create_and_save(self, data):
        message = self.model()
        message.user = data['user']
        message.room = data['room']
        message.content = data['content']
        message.save()

        return message

    def __chk_instance_data(self, pk, data):
        message = self.model.objects.get(pk=pk)

        _str = data.pop('str')

        for key, value in data.items():
            self.assertEqual(getattr(message, key), value)
        self.assertEqual(str(message), _str)

    def test_message_is_empty(self):
        self.assertEqual(self.model.objects.count(), 0)

    def test_create_message(self):
        content = 'message1'
        data = {
            'user': self.users[0],
            'room': self.room,
            'content': content,
        }
        _str = '{}: {}'.format(data['user'].username, content)
        expected = {
            'user': data['user'],
            'room': data['room'],
            'content': data['content'],
            'str': _str,
        }
        _message = self.__create_and_save(data)
        self.__chk_instance_data(_message.pk, expected)
        self.assertEqual(self.model.objects.count(), 1)

    def test_content_length_is_32(self):
        content = 'm' * 32
        data = {
            'user': self.users[0],
            'room': self.room,
            'content': content,
        }
        _str = '{}: {}'.format(data['user'].username, content)
        expected = {
            'user': data['user'],
            'room': data['room'],
            'content': data['content'],
            'str': _str,
        }
        _message = self.__create_and_save(data)
        self.__chk_instance_data(_message.pk, expected)
        self.assertEqual(self.model.objects.count(), 1)

    def test_content_length_is_33(self):
        content = 'm' * 32
        data = {
            'user': self.users[0],
            'room': self.room,
            'content': content + 'a',
        }
        _str = '{}: {}'.format(data['user'].username, content)
        expected = {
            'user': data['user'],
            'room': data['room'],
            'content': data['content'],
            'str': _str,
        }
        _message = self.__create_and_save(data)
        self.__chk_instance_data(_message.pk, expected)
        self.assertEqual(self.model.objects.count(), 1)
