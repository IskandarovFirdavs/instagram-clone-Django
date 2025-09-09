from django.db import models

from posts.models import PostModel
from users.models import UserModel


class Room(models.Model):
    CHAT_TYPE_CHOICES = [
        ('private', 'Private'),
        ('public', 'Public'),
    ]
    room_name = models.CharField(max_length=100, unique=True)
    members = models.ManyToManyField(UserModel, related_name='chats')
    chat_type = models.CharField(max_length=10, choices=CHAT_TYPE_CHOICES, default='public')

    def __str__(self):
        return self.room_name

    def can_add_member(self):
        if self.chat_type != 'private':
            return True
        if self.chat_type == 'private' and self.members.count() < 2:
            return True
        return False


class Message(models.Model):
    room = models.ForeignKey(Room, on_delete=models.CASCADE, related_name='messages')
    message = models.CharField(max_length=255)
    sender = models.ForeignKey(UserModel, on_delete=models.CASCADE)
    post = models.ForeignKey(PostModel, null=True, blank=True, on_delete=models.SET_NULL)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.sender} -> {self.room.room_name}'
