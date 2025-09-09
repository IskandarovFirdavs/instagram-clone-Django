from django.urls import path
from chat import views

urlpatterns = [
    path('', views.chat_view, name='chat'),
    path('home/', views.chats_list, name='chats'),
    path('<str:room_name>/', views.room_view, name='room'),
    path('another_profile/<str:username>/', views.another_user_profile_view, name='profile-another-chat'),
]
