from django.contrib import admin
from posts.models import PostModel, MusicModel, SingerModel, HashtagModel, PostLikeModel, CommentModel, \
    ReplyCommentModel, NotificationModel


class CommentInline(admin.TabularInline):
    model = CommentModel
    extra = 0
    readonly_fields = ('userID', 'created_at')

class ReplyCommentInline(admin.TabularInline):
    model = ReplyCommentModel
    extra = 0
    readonly_fields = ('userID', 'commentID', 'reply_comment', 'created_at')


class PostLikeInline(admin.TabularInline):
    model = PostLikeModel
    extra = 0
    readonly_fields = ('userID', 'created_at')


@admin.register(PostModel)
class PostModelAdmin(admin.ModelAdmin):
    list_display = ('id', 'caption', 'userID', 'post_type', 'since_created')
    list_filter = ('post_type', 'created_at')
    search_fields = ('caption', 'userID__username')
    inlines = [PostLikeInline, CommentInline, ReplyCommentInline]
    filter_horizontal = ('hashtags', 'music')
    readonly_fields = ('since_created', 'created_at')


@admin.register(HashtagModel)
class HashtagModelAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)


@admin.register(SingerModel)
class SingerModelAdmin(admin.ModelAdmin):
    list_display = ('full_name',)
    search_fields = ('full_name',)


@admin.register(MusicModel)
class MusicModelAdmin(admin.ModelAdmin):
    list_display = ('music_name', 'singer')
    search_fields = ('music_name', 'singer__full_name')
    list_filter = ('singer',)

admin.site.register(NotificationModel)
