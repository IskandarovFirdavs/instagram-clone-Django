from django.contrib import admin

from posts.models import PostModel, MusicModel, SingerModel, HashtagModel

admin.site.register(PostModel)
admin.site.register(MusicModel)
admin.site.register(SingerModel)
admin.site.register(HashtagModel)
