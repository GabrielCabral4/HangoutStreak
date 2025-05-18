from django.urls import path
from . import views

app_name = 'chat'

urlpatterns = [
    path('', views.inbox, name='inbox'),
    path('new/', views.new_chat, name='new_chat'),
    path('<int:chat_id>/', views.chat_detail, name='detail'),
    path('api/messages/<int:chat_id>/', views.load_messages, name='load_messages'),
    path('api/users/search/', views.search_users, name='search_users'),
] 