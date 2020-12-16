"""
This is a synchronous WebSocket consumer that accepts all connections, 
receives messages from its client, and echos those messages back to the same client. 
For now it does not broadcast messages to other clients in the same room.

Channels also supports writing asynchronous consumers for greater performance. 
However any asynchronous consumer must be careful to avoid directly performing 
blocking operations, such as accessing a Django model. See the Consumers reference 
for more information about writing asynchronous consumers:
    https://channels.readthedocs.io/en/stable/topics/consumers.html
"""

import json
from asgiref.sync import async_to_sync
from channels.generic.websocket import WebsocketConsumer


# https://channels.readthedocs.io/en/stable/tutorial/part_2.html


class ChatConsumer(WebsocketConsumer):
    def connect(self):
        self.room_name = self.scope['url_route']['kwargs']['room_name']
        self.room_group_name = 'chat_%s' % self.room_name

        # Join room group
        async_to_sync(self.channel_layer.group_add)(
            self.room_group_name, self.channel_name
        )

        self.accept()

    def disconnect(self, close_code):
        # Leave room group
        async_to_sync(self.channel_layer.group_discard)(
            self.room_group_name, self.channel_name
        )

    # Receive message from WebSocket
    def receive(self, text_data):
        text_data_json = json.loads(text_data)
        message = text_data_json['message']

        # Send message to room group
        async_to_sync(self.channel_layer.group_send)(
            self.room_group_name, {'type': 'chat_message', 'message': message}
        )

    # Receive message from room group
    def chat_message(self, event):
        message = event['message']

        # Send message to WebSocket
        self.send(text_data=json.dumps({'message': message}))
