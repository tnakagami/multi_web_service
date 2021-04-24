from channels.generic.websocket import AsyncJsonWebsocketConsumer
from channels.db import database_sync_to_async
from custom_templatetags.markdown_extras import markdown2html
import re
from datetime import datetime
from . import models

class ChatConsumer(AsyncJsonWebsocketConsumer):
    clients = {}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.group_name = ''
        self.room = None

    def get_current_time(self):
        return datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    def escape_process(self, message):
        text = markdown2html(message)
        escaped_text = re.sub('<\s*script\s*>(.*)<\s*/script\s*>', r'&lt;script&gt;\1&lt;/script&gt;', text.replace('"', '&quot;').replace("'", '&#39;'))
        return escaped_text

    def create_system_message(self, message):
        return '<font color="red">{}</font>'.format(message)

    async def connect(self):
        try:
            user = self.scope['user']
            pk = int(self.scope['url_route']['kwargs']['room_pk'])
            self.room = await database_sync_to_async(models.Room.objects.get)(pk=pk)
            ret = await database_sync_to_async(self.room.is_assigned)(user)
            self.group_name = 'chat-room{}'.format(pk)

            if ret:
                await self.accept()
                await self.channel_layer.group_add(self.group_name, self.channel_name)
                await self.channel_layer.group_send(
                    self.group_name,
                    {
                        'type': 'system_message',
                        'is_connected': True,
                        'target_username': user.username,
                        'target_viewname': user.viewname,
                    }
                )
        except Exception as e:
            raise Exception(e)

    async def disconnect(self, close_code):
        user = self.scope['user']

        await self.channel_layer.group_send(
            self.group_name,
            {
                'type': 'system_message',
                'is_connected': False,
                'target_username': user.username,
                'target_viewname': user.viewname,
            }
        )
        await self.channel_layer.group_discard(self.group_name, self.channel_name)
        await self.close()

    # receive message from WebSocket
    async def receive_json(self, content):
        try:
            await self.create_message(content)
            await self.channel_layer.group_send(
                self.group_name,
                {
                    'type': 'chat_message',
                    'username': content['username'],
                    'viewname': content['viewname'],
                    'message': content['message'],
                }
            )
        except Exception as e:
            raise Exception(e)

    # send message by system
    async def system_message(self, event):
        try:
            is_connected = event['is_connected']
            target_username = event['target_username']
            target_viewname = event['target_viewname']
            current_time = self.get_current_time()

            if is_connected:
                self.clients[target_username] = target_viewname
                message_type = 'connect'
                message = '{}さんが参加しました'.format(target_username)
            else:
                del self.clients[target_username]
                message_type = 'disconnect'
                message = '{}さんが退場しました'.format(target_username)

            await self.send_json(content={
                'type': message_type,
                'target_username': target_username,
                'target_viewname': target_viewname,
                'viewname': '',
                'username': self.create_system_message('system'),
                'datetime': current_time,
                'message': self.create_system_message(message),
                'members': self.clients,
            })
        except Exception as e:
            raise Exception(e)

    # send message to clients
    async def chat_message(self, event):
        try:
            username = event['username']
            viewname = event['viewname']
            message = self.escape_process(event['message'])
            current_time = self.get_current_time()
            await self.send_json(content={
                'type': 'on_message',
                'viewname': viewname,
                'username': username,
                'datetime': current_time,
                'message': message,
            })
        except Exception as e:
            raise Exception(e)

    @database_sync_to_async
    def create_message(self, event):
        try:
            models.Message.objects.create(
                user=self.scope['user'],
                room=self.room,
                content=event['message'],
            )
        except Exception as e:
            raise Exception(e)
