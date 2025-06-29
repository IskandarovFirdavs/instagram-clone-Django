from django.contrib.auth.models import AbstractUser
from django.db import models

class UserModel(AbstractUser):
    full_name = models.CharField(max_length=150)
    bio = models.CharField(max_length=255, null=True, blank=True)
    avatar = models.ImageField(upload_to='user/avatars/', null=True, blank=True)

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
