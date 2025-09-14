# chat/consumers.py
import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from .models import Room, Message, UserModel
from posts.models import PostModel  # agar kerak bo'lsa

class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        # room_name from URL, e.g. "private_admin_jamil"
        self.room_name = self.scope['url_route']['kwargs']['room_name']
        # group name used for channel_layer
        self.room_group_name = f"room_{self.room_name}"

        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )
        await self.accept()

    async def disconnect(self, code):
        # use the group name (not raw room_name)
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    async def receive(self, text_data):
        # data expected: {"message": "...", "room_name": "...", "sender": "..."}
        data_json = json.loads(text_data)

        event = {"type": "send_message", "message": data_json}

        # send to the group (use same group name as added)
        await self.channel_layer.group_send(self.room_group_name, event)

    async def send_message(self, event):
        data = event["message"]

        # save to DB (text or post)
        await self.create_message(data)

        # build response for clients
        if data.get("post_id"):
            response = {
                "sender": data.get("sender"),
                "post_id": data.get("post_id"),
                "post_type": data.get("post_type"),
                "caption": data.get("caption"),
                "media_url": data.get("media_url"),
                "username": data.get("username"),
            }
        else:
            response = {
                "sender": data.get("sender"),
                "message": data.get("message"),
            }

        await self.send(text_data=json.dumps({"message": response}))

    @database_sync_to_async
    def create_message(self, data):
        # find room by room_name (string)
        try:
            room = Room.objects.get(room_name=data.get("room_name") or self.room_name)
        except Room.DoesNotExist:
            return

        # find sender user
        try:
            sender_user = UserModel.objects.get(username=data.get('sender'))
        except UserModel.DoesNotExist:
            return

        # if this is a post share
        if data.get("post_id"):
            try:
                post = PostModel.objects.get(id=data.get("post_id"))
            except Exception:
                post = None
            # create message with post attached
            Message.objects.create(room=room, sender=sender_user, post=post)
            return

        # else if text message
        text = data.get("message")
        if text:
            # optional: prevent exact duplicate messages (your previous logic)
            if not Message.objects.filter(message=text, sender=sender_user, room=room).exists():
                Message.objects.create(room=room, message=text, sender=sender_user)
