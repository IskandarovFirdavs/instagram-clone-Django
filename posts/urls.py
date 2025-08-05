from django.urls import path
from posts import views

urlpatterns = [
    path('', views.home_view, name='home'),
    path('create/', views.post_create, name='create'),
    path('direct/', views.DirectView.as_view(), name='direct'),
    path('explore/', views.explore_view, name='explore'),
    path('messages/', views.MessagesView.as_view(), name='messages'),
    path('notifications/', views.notification_view, name='notifications'),
    path('reels/', views.reels_view, name='reels'),
    path('like/<int:id>/', views.like_create, name='like'),
    path('home_comment/<int:comment_id>/', views.home_comment_like, name='home-comment-like'),
    path('comment/<int:comment_id>/', views.like_comment, name='comment-like'),
    path('reply_comment/<int:id>/', views.like_reply_comment, name='reply-comment-like'),
    path('home_reply_comment/<int:id>/', views.home_reply_comment_like, name='home-reply-comment-like'),
    path('saved/', views.SavedListView.as_view(), name="saved"),
    path("saved/<int:id>/", views.create_saved_video, name="saved-create"),
]