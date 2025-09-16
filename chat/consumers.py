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

    # consumers.py - Fix the create_message method
    # consumers.py - Ensure proper message saving for posts
    @database_sync_to_async
    def create_message(self, data):
        try:
            room = Room.objects.get(room_name=data.get("room_name") or self.room_name)
            sender_user = UserModel.objects.get(username=data.get('sender'))

            # If this is a post share
            if data.get("post_id"):
                try:
                    post = PostModel.objects.get(id=data.get("post_id"))
                    # Create message with post attached - this ensures persistence
                    message_obj = Message.objects.create(
                        room=room,
                        sender=sender_user,
                        post=post,
                        message=data.get("message", f"Shared a {post.post_type}")
                    )
                    # Return the complete data for WebSocket broadcast
                    return {
                        "id": message_obj.id,
                        "sender": sender_user.username,
                        "post_id": post.id,
                        "post_type": post.post_type,
                        "caption": post.caption,
                        "media_url": post.contentUrl.url,
                        "username": post.userID.username,
                        "message": data.get("message", f"Shared a {post.post_type}")
                    }
                except PostModel.DoesNotExist:
                    # Fallback if post doesn't exist
                    message_obj = Message.objects.create(
                        room=room,
                        sender=sender_user,
                        message=data.get("message", "Shared content")
                    )
                    return {"sender": sender_user.username, "message": data.get("message", "Shared content")}
            else:
                # Regular text message
                text = data.get("message")
                if text:
                    message_obj = Message.objects.create(room=room, message=text, sender=sender_user)
                    return {"sender": sender_user.username, "message": text}

        except (Room.DoesNotExist, UserModel.DoesNotExist):
            return None
