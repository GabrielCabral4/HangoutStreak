from django.contrib import admin
from .models import Event

@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display = ('title', 'date', 'creator', 'is_past')
    list_filter = ('date', 'creator')
    search_fields = ('title', 'description')
    date_hierarchy = 'date'
