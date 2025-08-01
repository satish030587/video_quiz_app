from django.db import models
from django.contrib.auth.models import AbstractUser
from videos.models import Video

class User(AbstractUser):
    email = models.EmailField(unique=True)
    is_superadmin = models.BooleanField(default=False)
    date_joined = models.DateTimeField(auto_now_add=True)
    last_login = models.DateTimeField(auto_now=True)
    profile_picture = models.ImageField(upload_to='profile_pics/', null=True, blank=True)
    
    class Meta:
        db_table = 'users'

class UserProgress(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='progress')
    videos_passed = models.ManyToManyField(Video, related_name='passed_by_users', blank=True)
    videos_failed = models.ManyToManyField(Video, related_name='failed_by_users', blank=True)
    total_retries = models.IntegerField(default=0)
    overall_progress = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    last_updated = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'user_progress'
        
    def __str__(self):
        return f"{self.user.username}'s Progress"
    
    def recalculate_progress(self):
        """Calculate overall progress based on passed videos"""
        from videos.models import Video
        total_videos = Video.objects.filter(is_active=True).count()
        passed_videos = self.videos_passed.count()
        
        if total_videos > 0:
            self.overall_progress = (passed_videos / total_videos) * 100
        else:
            self.overall_progress = 0
            
        self.save()
        return {
            'overall_progress': self.overall_progress,
            'videos_passed': passed_videos,
            'total_videos': total_videos
        }
    
    def reset_progress(self):
        """Reset all progress for this user"""
        self.videos_passed.clear()
        self.videos_failed.clear()
        self.total_retries = 0
        self.overall_progress = 0
        self.save()
    
    def sync_with_quiz_attempts(self):
        """Sync the videos_passed with successful quiz attempts"""
        from quizzes.models import QuizAttempt
        
        # Get all passed attempts for this user
        passed_attempts = QuizAttempt.objects.filter(
            user=self.user,
            is_passed=True
        )
        
        # Add all videos from passed attempts to videos_passed
        for attempt in passed_attempts:
            if attempt.video not in self.videos_passed.all():
                self.videos_passed.add(attempt.video)
                
        # Remove videos from videos_passed that don't have passed attempts
        passed_video_ids = passed_attempts.values_list('video', flat=True)
        for video in self.videos_passed.all():
            if video.id not in passed_video_ids:
                self.videos_passed.remove(video)
                
        # Update total retries
        self.total_retries = QuizAttempt.objects.filter(
            user=self.user,
            attempt_number__gt=1
        ).count()
        
        # Recalculate overall progress
        return self.recalculate_progress()
        
    @classmethod
    def recalculate_all_progress(cls):
        """Recalculate progress for all users"""
        updated_count = 0
        for progress in cls.objects.all():
            progress.recalculate_progress()
            updated_count += 1
        return updated_count

class Certificate(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='certificates')
    unique_id = models.CharField(max_length=50, unique=True)
    issue_date = models.DateTimeField(auto_now_add=True)
    pdf_file = models.FileField(upload_to='certificates/', null=True, blank=True)
    is_downloaded = models.BooleanField(default=False)
    
    class Meta:
        db_table = 'certificates'
        
    def __str__(self):
        return f"{self.user.username}'s Certificate ({self.unique_id})"
