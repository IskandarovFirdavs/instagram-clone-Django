from django.utils import timezone

from django.core.validators import MinLengthValidator
from django.db import models

from users.models import UserModel


class PostModel(models.Model):
    class PostTypeChoice(models.TextChoices):
        History = 'HISTORY', 'History'
        Post = 'POST', 'Post'
        Reels = 'REELS', 'Reels'

    caption = models.CharField(max_length=255)
    userID = models.ForeignKey(UserModel, on_delete=models.CASCADE, related_name='user')
    post_type = models.CharField(max_length=8, choices=PostTypeChoice)
    contentUrl = models.FileField(upload_to='posts')
    tagging = models.ForeignKey(UserModel, on_delete=models.CASCADE, related_name='tagging', null=True, blank=True)
    latitude = models.FloatField(
        null=True, blank=True
    )
    longitude = models.FloatField(
        null=True, blank=True
    )
    hashtags = models.ManyToManyField('HashtagModel', blank=True, null=True)
    music = models.ManyToManyField('MusicModel', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def since_created(self):
        now = timezone.now()
        diff = now - self.created_at

        days = diff.days
        seconds = diff.seconds

        if days > 0:
            return f"{days} day{'s' if days > 1 else ''} ago"
        elif seconds >= 3600:
            hours = seconds // 3600
            return f"{hours} hour{'s' if hours > 1 else ''} ago"
        elif seconds >= 60:
            minutes = seconds // 60
            return f"{minutes} minute{'s' if minutes > 1 else ''} ago"
        else:
            return "Just now"


class HashtagModel(models.Model):
    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return f'#{self.name}'


class SingerModel(models.Model):
    full_name = models.CharField(max_length=100)


class MusicModel(models.Model):
    singer = models.ForeignKey(SingerModel, on_delete=models.CASCADE)
    music_name = models.CharField(max_length=100)
    file = models.FileField(upload_to='music')


class PostLikeModel(models.Model):
    postID = models.ForeignKey(PostModel, on_delete=models.CASCADE)
    userID = models.ForeignKey(UserModel, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)


class CommentModel(models.Model):
    postID = models.ForeignKey(PostModel, on_delete=models.CASCADE)
    userID = models.ForeignKey(UserModel, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
