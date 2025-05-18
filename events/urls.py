from django.urls import path
from . import views

app_name = 'events'

urlpatterns = [
    path('', views.event_list, name='list'),
    path('create/', views.event_create, name='create'),
    path('<int:event_id>/', views.event_detail, name='detail'),
    path('<int:event_id>/edit/', views.event_edit, name='edit'),
    path('<int:event_id>/delete/', views.event_delete, name='delete'),
    path('<int:event_id>/join/', views.event_join, name='join'),
    path('<int:event_id>/leave/', views.event_leave, name='leave'),
    path('<int:event_id>/photos/', views.event_photos, name='event_photos'),
    path('photos/<int:photo_id>/delete/', views.delete_event_photo, name='delete_photo'),
] 