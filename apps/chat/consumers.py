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
from channels.generic.websocket import WebsocketConsumer


class ChatConsumer(WebsocketConsumer):
    def connect(self):
        self.accept()

    def disconnect(self, close_code):
        pass

    def receive(self, text_data):
        text_data_json = json.loads(text_data)
        message = text_data_json['message']

        self.send(text_data=json.dumps({'message': message}))
