from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from custom_templatetags.blog_extras import markdown2html
import json
from . import models
from datetime import datetime

class ChatConsumer(AsyncWebsocketConsumer):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.group_name = ''
        self.pk = -1

    def get_current_time(self):
        return datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    def escape_process(self, message):
        text = markdown2html(message)
        return text.replace('<script>', '&lt;script&gt;').replace('</script>', '&lt;/script&gt;')

    async def connect(self):
        try:
            user = self.scope['user']
            self.pk = int(self.scope['url_route']['kwargs']['room_pk'])
            self.group_name = 'chat-room{}'.format(self.pk)
            await self.accept()
            await self.channel_layer.group_add(self.group_name, self.channel_name)
        except Exception as e:
            raise Exception(e)

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(self.group_name, self.channel_name)
        await self.close()

    # receive message from WebSocket
    async def receive(self, text_data):
        try:
            event = json.loads(text_data)
            username = event['username']
            viewname = event['viewname']
            message = self.escape_process(event['message'])
            current_time = self.get_current_time()
            await self.create_message(event)
            await self.channel_layer.group_send(
                self.group_name,
                {
                    'type': 'chat_message',
                    'viewname': viewname,
                    'username': username,
                    'datetime': current_time,
                    'message': message,
                }
            )
        except Exception as e:
            raise Exception(e)

    # receive message from room group
    async def chat_message(self, event):
        try:
            username = event['username']
            viewname = event['viewname']
            message = self.escape_process(event['message'])
            current_time = self.get_current_time()
            await self.send(text_data=json.dumps({
                'type': 'chat_message',
                'viewname': viewname,
                'username': username,
                'datetime': current_time,
                'message': message,
            }))
        except Exception as e:
            raise Exception(e)

    @database_sync_to_async
    def create_message(self, event):
        try:
            room = models.Room.objects.get(pk=self.pk)
            models.Message.objects.create(
                user=self.scope['user'],
                room=room,
                content=event['message'],
            )
        except Exception as e:
            raise Exception(e)
