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
    saved = models.ManyToManyField(UserModel, blank=True, null=True, related_name='saved')
    created_at = models.DateTimeField(auto_now_add=True)

    def since_created(self):
        now = timezone.now()
        diff = now - self.created_at

        days = diff.days
        seconds = diff.seconds

        if days >= 7:
            weeks = days // 7
            return f"{weeks} week{'s' if weeks > 1 else ''} ago"
        elif days > 0:
            return f"{days} day{'s' if days > 1 else ''} ago"
        elif seconds >= 3600:
            hours = seconds // 3600
            return f"{hours} hour{'s' if hours > 1 else ''} ago"
        elif seconds >= 60:
            minutes = seconds // 60
            return f"{minutes} minute{'s' if minutes > 1 else ''} ago"
        else:
            return "Just now"

    def comments_count(self):
        return self.comments.count() + self.reply_comments.count()

    def likes_count(self):
        return self.likes.count()

    def location(self):
        return f"{self.latitude},{self.longitude}"


class HashtagModel(models.Model):
    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return f'#{self.name}'


class PostLikeModel(models.Model):
    postID = models.ForeignKey(PostModel, on_delete=models.CASCADE, related_name='likes')
    userID = models.ForeignKey(UserModel, on_delete=models.CASCADE, related_name='likes')
    created_at = models.DateTimeField(auto_now_add=True)


class SingerModel(models.Model):
    full_name = models.CharField(max_length=100)


class MusicModel(models.Model):
    singer = models.ForeignKey(SingerModel, on_delete=models.CASCADE, related_name='musics')
    music_name = models.CharField(max_length=100)
    file = models.FileField(upload_to='music')


class CommentModel(models.Model):
    postID = models.ForeignKey(PostModel, on_delete=models.CASCADE, related_name='comments')
    userID = models.ForeignKey(UserModel, on_delete=models.CASCADE, related_name='comments')
    comment = models.CharField(max_length=250)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'Comment by {self.userID} on {self.postID}'

    def since_created(self):
        now = timezone.now()
        diff = now - self.created_at

        days = diff.days
        seconds = diff.seconds

        if days > 7:
            weeks = days // 7
            return f"{weeks} week{'s' if weeks > 2 else ''} ago"
        elif days > 0:
            return f"{days} day{'s' if days > 1 else ''} ago"
        elif seconds >= 3600:
            hours = seconds // 3600
            return f"{hours} hour{'s' if hours > 1 else ''} ago"
        elif seconds >= 60:
            minutes = seconds // 60
            return f"{minutes} minute{'s' if minutes > 1 else ''} ago"
        else:
            return "Just now"

    def comment_likes_count(self):
        return self.comment_likes.count()

    def replies_count(self):
        return self.reply_comments.count()


class CommentLikeModel(models.Model):
    commentID = models.ForeignKey(CommentModel, on_delete=models.CASCADE, related_name='comment_likes')
    userID = models.ForeignKey(UserModel, on_delete=models.CASCADE, related_name='comment_likes')
    created_at = models.DateTimeField(auto_now_add=True)


class ReplyCommentModel(models.Model):
    postID = models.ForeignKey(PostModel, on_delete=models.CASCADE, related_name='reply_comments')
    commentID = models.ForeignKey(CommentModel, on_delete=models.CASCADE, related_name='reply_comments')
    userID = models.ForeignKey(UserModel, on_delete=models.CASCADE, related_name='reply_comments')
    reply_comment = models.CharField(max_length=250)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'Reply_comment by {self.userID} on {self.commentID}'

    def since_created(self):
        now = timezone.now()
        diff = now - self.created_at

        days = diff.days
        seconds = diff.seconds

        if days > 7:
            weeks = days // 7
            return f"{weeks} week{'s' if weeks > 2 else ''} ago"
        elif days > 0:
            return f"{days} day{'s' if days > 1 else ''} ago"
        elif seconds >= 3600:
            hours = seconds // 3600
            return f"{hours} hour{'s' if hours > 1 else ''} ago"
        elif seconds >= 60:
            minutes = seconds // 60
            return f"{minutes} minute{'s' if minutes > 1 else ''} ago"
        else:
            return "Just now"

    def reply_comment_likes_count(self):
        return self.reply_comment_likes.count()


class ReplyCommentLikeModel(models.Model):
    reply_commentID = models.ForeignKey(ReplyCommentModel, on_delete=models.CASCADE, related_name='reply_comment_likes')
    userID = models.ForeignKey(UserModel, on_delete=models.CASCADE, related_name='reply_comment_likes')
    created_at = models.DateTimeField(auto_now_add=True)


class NotificationModel(models.Model):
    owner = models.ForeignKey(UserModel, on_delete=models.CASCADE, related_name='notifications_owner')
    post_like = models.ForeignKey(PostModel, on_delete=models.CASCADE, related_name='notifications', null=True,
                                  blank=True, default=None)
    comment_like = models.ForeignKey(CommentModel, on_delete=models.CASCADE, related_name='notifications', null=True,
                                     blank=True, default=None)
    reply_comment_like = models.ForeignKey(ReplyCommentModel, on_delete=models.CASCADE, related_name='notifications',
                                           null=True, blank=True, default=None)
    liked_by = models.ForeignKey(UserModel, on_delete=models.CASCADE, related_name='notifications_liked_by')

    created_at = models.DateTimeField(auto_now_add=True)

    def since_created(self):
        now = timezone.now()
        diff = now - self.created_at

        days = diff.days
        seconds = diff.seconds

        if days > 7:
            weeks = days // 7
            return f"{weeks} week{'s' if weeks > 2 else ''} ago"
        elif days > 0:
            return f"{days} day{'s' if days > 1 else ''} ago"
        elif seconds >= 3600:
            hours = seconds // 3600
            return f"{hours} hour{'s' if hours > 1 else ''} ago"
        elif seconds >= 60:
            minutes = seconds // 60
            return f"{minutes} minute{'s' if minutes > 1 else ''} ago"
        else:
            return "Just now"

