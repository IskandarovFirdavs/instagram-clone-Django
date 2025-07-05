from django.urls import path
from posts import views

urlpatterns = [
    path('', views.home_view, name='home'),
    path('create/', views.post_create, name='create'),
    path('direct/', views.DirectView.as_view(), name='direct'),
    path('explore/', views.explore_view, name='explore'),
    path('messages/', views.MessagesView.as_view(), name='messages'),
    path('notifications/', views.NotificationsView.as_view(), name='notifications'),
    path('reels/', views.ReelsView.as_view(), name='reels'),
    path('search/', views.SearchView.as_view(), name='search'),
]
