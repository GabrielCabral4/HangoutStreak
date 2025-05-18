from django.contrib import admin
from .models import Profile

@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'streak_count', 'total_events')
    search_fields = ('user__username', 'bio')
    list_filter = ('streak_count', 'total_events')
