import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from .models import Room, Message, UserModel


class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.room_name = f"room_{self.scope['url_route']['kwargs']['room_name']}"
        await self.channel_layer.group_add(self.room_name, self.channel_name)

        await self.accept()

    async def disconnect(self, code):
        await self.channel_layer.group_discard(self.room_name, self.channel_name)
        self.close(code)

    async def receive(self, text_data):
        data_json = json.loads(text_data)

        event = {"type": "send_message", "message": data_json}

        await self.channel_layer.group_send(self.room_name, event)

    async def send_message(self, event):
        data = event["message"]
        await self.create_message(data=data)

        response = {"sender": data["sender"], "message": data["message"]}

        await self.send(text_data=json.dumps({"message": response}))

    @database_sync_to_async
    def create_message(self, data):
        get_room = Room.objects.get(room_name=data["room_name"])

        try:
            sender_user = UserModel.objects.get(username=data['sender'])
        except UserModel.DoesNotExist:
            return


        if not Message.objects.filter(
                message=data["message"], sender=sender_user
        ).exists():
            new_message = Message.objects.create(
                room=get_room, message=data["message"], sender=sender_user
            )
