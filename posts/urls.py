from django.urls import path
from posts import views

urlpatterns = [
    path('', views.home_view, name='home'),
    path('create/', views.post_create, name='create'),
    path('direct/', views.DirectView.as_view(), name='direct'),
    path('explore/', views.explore_view, name='explore'),
    path('messages/', views.MessagesView.as_view(), name='messages'),
    path('notifications/', views.NotificationsView.as_view(), name='notifications'),
    path('reels/', views.reels_view, name='reels'),
    path('like/<int:id>/', views.like_create, name='like'),
    path('comment/<int:id>/', views.like_comment, name='comment-like'),
    path('reply_comment/<int:id>/', views.like_reply_comment, name='reply-comment-like'),
    path('saved/', views.SavedListView.as_view(), name="saved"),
    path("saved/<int:id>/", views.create_saved_video, name="saved-create"),
    path('search/', views.UserListView.as_view(), name='search'),
]
