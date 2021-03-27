from django.test import TestCase
from channels.testing.websocket import WebsocketCommunicator
from channels.db import database_sync_to_async
from django.test.utils import override_settings
from registration.tests.factories import UserFactory
from chat.tests.factories import RoomFactory, MessageFactory
from chat import consumers, models

import warnings
warnings.simplefilter('ignore', RuntimeWarning)
# [Warning]
# RuntimeWarning: coroutine 'ChatConsumerTests.***' was never awaited: method()
# RuntimeWarning: Enable tracemalloc to get the object allocation traceback

class ChatConsumerTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

    @classmethod
    def setUpTestData(cls):
        cls.password = 'password'
        cls.users = UserFactory.create_batch(5)
        cls.room = RoomFactory.create(owner=cls.users[0], name='chat_room', assigned=[cls.users[1], cls.users[2]]) # invalid: user[3], user[4]

    def __create_communicator(self):
        communicator = WebsocketCommunicator(consumers.ChatConsumer.as_asgi(), '/ws/room/{}'.format(self.room.pk))
        return communicator

    def setUp(self):
        self.communicator = self.__create_communicator()

    @override_settings(AXES_ENABLED=False)
    @database_sync_to_async
    async def test_connection_owner(self):
        await self.async_client.login(username=self.users[0].username, password=self.password)
        connected, _ = await self.communicator.connect()
        self.assertTrue(connected)
        self.assertEqual(self.communicator.group_name, 'chat-room{}'.format(self.room.pk))
        self.assertEqual(self.communicator.scope['user'], self.users[0])
        await self.communicator.disconnect()

    @override_settings(AXES_ENABLED=False)
    @database_sync_to_async
    async def test_connection_is_assigned_user1(self):
        await self.client.login(username=self.users[1].username, password=self.password)
        connected, _ = await self.communicator.connect()
        self.assertTrue(connected)
        self.assertEqual(self.communicator.group_name, 'chat-room{}'.format(self.room.pk))
        await self.communicator.disconnect()

    @override_settings(AXES_ENABLED=False)
    @database_sync_to_async
    async def test_connection_is_not_assigned_user4(self):
        await self.client.login(username=self.users[4].username, password=self.password)
        connected, _ = await self.communicator.connect()
        self.assertFalse(connected)
        self.assertEqual(self.communicator.group_name, 'chat-room{}'.format(self.room.pk))
        await self.communicator.disconnect()

    @override_settings(AXES_ENABLED=False)
    @database_sync_to_async
    async def test_send_receive_own_message(self):
        await self.async_client.login(username=self.users[0].username, password=self.password)
        connected, _ = await self.communicator.connect()
        self.assertTrue(connected)
        data = {
            'username': self.users[0].username,
            'viewname': self.users[0].viewname,
            'message': 'hello world',
        }
        await self.communicator.send_json_to(data)
        response = await self.communicator.receive_json_from()
        await self.communicator.disconnect()

        # check
        for key in ['type', 'username', 'viewname', 'datetime', 'message']:
            self.assertEqual(key in response.keys())
        for key, value in data.items():
            self,assertEqual(response[key], value)
        queryset = await models.Message.objects.all()
        self.assertEqual(queryset.count(), 1)
        message = queryset.first()
        self.assertEqual(message.user, self.users[0])
        self.assertEqual(message.room, self.room)
        self.assertEqual(message.context, data['message'])

    @override_settings(AXES_ENABLED=False)
    @database_sync_to_async
    async def test_send_message_receive_other_user(self):
        await self.async_client.login(username=self.users[0].username, password=self.password)
        connected, _ = await self.communicator.connect()
        self.assertTrue(connected)
        self.async_client.logout()
        await self.async_client.login(username=self.users[1].username, password=self.password)
        communicator = self.__create_communicator()
        connected, _ = await communicator.connect()
        self.assertTrue(connected)

        data = {
            'username': self.users[0].username,
            'viewname': self.users[0].viewname,
            'message': 'hello world',
        }
        await self.communicator.send_json_to(data)
        response_owner = await self.communicator.receive_json_from()
        response_other = await      communicator.receive_json_from()
        await self.communicator.disconnect()
        await      communicator.disconnect()

        # check
        for key, value in data.items():
            self,assertEqual(response_owner[key], value)
            self,assertEqual(response_other[key], value)
        queryset = await models.Message.objects.all()
        self.assertEqual(queryset.count(), 1)
        message = queryset.first()
        self.assertEqual(message.user, self.users[0])
        self.assertEqual(message.room, self.room)
        self.assertEqual(message.context, data['message'])

    @override_settings(AXES_ENABLED=False)
    @database_sync_to_async
    async def test_receive_message_from_other_user(self):
        await self.async_client.login(username=self.users[0].username, password=self.password)
        connected, _ = await self.communicator.connect()
        self.assertTrue(connected)
        self.async_client.logout()
        await self.async_client.login(username=self.users[1].username, password=self.password)
        communicator = self.__create_communicator()
        connected, _ = await communicator.connect()
        self.assertTrue(connected)

        data = {
            'username': self.users[1].username,
            'viewname': self.users[1].viewname,
            'message': 'hello world from other user',
        }
        await communicator.send_json_to(data)
        response_owner = await self.communicator.receive_json_from()
        response_other = await      communicator.receive_json_from()
        await self.communicator.disconnect()
        await      communicator.disconnect()

        # check
        for key, value in data.items():
            self,assertEqual(response_owner[key], value)
            self,assertEqual(response_other[key], value)
        queryset = await models.Message.objects.all()
        self.assertEqual(queryset.count(), 1)
        message = queryset.first()
        self.assertEqual(message.user, self.users[1])
        self.assertEqual(message.room, self.room)
        self.assertEqual(message.context, data['message'])

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
