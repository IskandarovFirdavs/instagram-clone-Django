from django.contrib.auth.models import AbstractUser
from django.db import models


class UserModel(AbstractUser):
    bio = models.CharField(max_length=255, null=True, blank=True)
    avatar = models.ImageField(upload_to='user/avatars/', null=True, blank=True)
    website = models.URLField(null=True, blank=True)

    class GenderChoice(models.TextChoices):
        MALE = 'MALE', 'Male'
        FEMALE = 'FEMALE', 'Female'
        NOT_GIVEN = "NOT_GIVEN", "Not given"

    gender = models.CharField(
        max_length=10,
        choices=GenderChoice.choices,
        default=GenderChoice.NOT_GIVEN,
        null=True,
        blank=True
    )

    @property
    def followers_count(self):
        return self.follower_set.count()

    @property
    def following_count(self):
        return self.following_set.count()

    def is_following(self, user):
        return self.following_set.filter(following=user).exists()

    def is_follower(self, user):
        return self.follower_set.fitler(follower=user).exists()


class Follow(models.Model):
    follower = models.ForeignKey(
        UserModel,
        on_delete=models.CASCADE,
        related_name='following_set'
    )
    following = models.ForeignKey(
        UserModel,
        on_delete=models.CASCADE,
        related_name='follower_set'
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('follower', 'following',)
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.follower.username} -> {self.following.username}'
