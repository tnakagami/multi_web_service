from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from custom_templatetags.markdown_extras import markdown2html
import json
import re
from datetime import datetime
from . import models

class ChatConsumer(AsyncWebsocketConsumer):
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

    async def connect(self):
        try:
            user = self.scope['user']
            pk = int(self.scope['url_route']['kwargs']['room_pk'])
            self.room = await database_sync_to_async(models.Room.objects.get)(pk=pk)
            self.group_name = 'chat-room{}'.format(pk)

            if self.room.is_assigned(user):
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
            models.Message.objects.create(
                user=self.scope['user'],
                room=self.room,
                content=event['message'],
            )
        except Exception as e:
            raise Exception(e)
