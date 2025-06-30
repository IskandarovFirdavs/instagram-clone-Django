from django.contrib import admin
from users.models import UserModel, Follow

admin.site.register(UserModel)
admin.site.register(Follow)
