# In videos/admin.py

from django.contrib import admin
from .models import Video

@admin.register(Video)
class VideoAdmin(admin.ModelAdmin):
    list_display = ('title', 'sequence_number', 'duration', 'passing_percentage', 'time_limit', 'is_active')
    list_filter = ('is_active',)
    search_fields = ('title', 'description')