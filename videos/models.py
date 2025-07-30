# In videos/models.py

from django.db import models

class Video(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField()
    video_file = models.FileField(upload_to='videos/', null=True, blank=True)
    video_url = models.URLField(null=True, blank=True)
    duration = models.IntegerField(help_text="Duration in seconds")
    sequence_number = models.IntegerField(help_text="Order in which videos appear")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    passing_percentage = models.IntegerField(default=70)
    time_limit = models.IntegerField(help_text="Quiz time limit in minutes")
    is_active = models.BooleanField(default=True)
    
    class Meta:
        db_table = 'videos'
        ordering = ['sequence_number']
        
    def __str__(self):
        return self.title