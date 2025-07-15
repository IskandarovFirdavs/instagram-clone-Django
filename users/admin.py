from django.contrib import admin
from users.models import UserModel, Follow

@admin.register(UserModel)
class UserModelAdmin(admin.ModelAdmin):
    list_display = ('username', 'email', 'gender', 'followers_count', 'following_count', 'is_staff')
    search_fields = ('username', 'email')
    list_filter = ('gender', 'is_staff', 'is_superuser')
    readonly_fields = ('last_login', 'date_joined')

@admin.register(Follow)
class FollowAdmin(admin.ModelAdmin):
    list_display = ('follower', 'following', 'created_at')
    search_fields = ('follower__username', 'following__username')
    list_filter = ('created_at',)
