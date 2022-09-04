"""
Consumers for the chat app.

Consumers are used to structure code as a series of functions to be called
whenever an event happens, rather than requiring you to write an event loop.
https://channels.readthedocs.io/en/stable/topics/consumers.html
"""

import json

from asgiref.sync import async_to_sync
from channels.generic.websocket import WebsocketConsumer

# https://channels.readthedocs.io/en/stable/tutorial/part_2.html


class ChatConsumer(WebsocketConsumer):
    """Websocket consumer for chats."""

    def connect(self):
        """Join room group."""
        self.room_name = self.scope['url_route']['kwargs']['room_name']
        self.room_group_name = f'chat_{self.room_name}'
        async_to_sync(self.channel_layer.group_add)(self.room_group_name, self.channel_name)
        self.accept()

    def disconnect(self, close_code):
        """Leave room group."""
        async_to_sync(self.channel_layer.group_discard)(
            self.room_group_name, self.channel_name
        )

    def receive(self, text_data):
        """Receive message from WebSocket."""
        text_data_json = json.loads(text_data)
        message = text_data_json['message']

        # Send message to room group
        async_to_sync(self.channel_layer.group_send)(
            self.room_group_name, {'type': 'chat_message', 'message': message}
        )

    def chat_message(self, event):
        """Receive message from room group."""
        message = event['message']

        # Send message to WebSocket
        self.send(text_data=json.dumps({'message': message}))
