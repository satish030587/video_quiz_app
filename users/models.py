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
        """Recalculate user progress based on current quiz attempts"""
        from quizzes.models import QuizAttempt
        
        # Get all passed and failed videos
        passed_videos = []
        failed_videos = []
        total_retries = 0
        
        # Get all videos
        all_videos = Video.objects.filter(is_active=True)
        
        for video in all_videos:
            # Get all attempts for this video by this user
            attempts = QuizAttempt.objects.filter(
                user=self.user, 
                video=video,
                status='completed'
            ).order_by('attempt_number')
            
            if attempts.exists():
                # Count retries (attempts beyond the first one)
                total_retries += max(0, attempts.count() - 1)
                
                # Check if user has passed this video
                passed_attempt = attempts.filter(is_passed=True).first()
                if passed_attempt:
                    passed_videos.append(video)
                else:
                    # Check if user has exhausted all attempts (2 attempts max)
                    if attempts.count() >= 2:
                        failed_videos.append(video)
        
        # Update the many-to-many relationships
        self.videos_passed.set(passed_videos)
        self.videos_failed.set(failed_videos)
        self.total_retries = total_retries
        
        # Calculate overall progress
        total_videos = all_videos.count()
        passed_count = len(passed_videos)
        self.overall_progress = (passed_count / total_videos * 100) if total_videos > 0 else 0
        
        self.save()
        return {
            'passed_videos': passed_count,
            'failed_videos': len(failed_videos),
            'total_retries': total_retries,
            'overall_progress': float(self.overall_progress)
        }
    
    def reset_progress(self):
        """Reset user progress and delete all quiz attempts"""
        from quizzes.models import QuizAttempt
        
        # Delete all quiz attempts for this user
        QuizAttempt.objects.filter(user=self.user).delete()
        
        # Clear progress
        self.videos_passed.clear()
        self.videos_failed.clear()
        self.total_retries = 0
        self.overall_progress = 0
        self.save()
        
        return True
    
    @classmethod
    def update_user_progress(cls, user):
        """Class method to update progress for a specific user"""
        progress, created = cls.objects.get_or_create(user=user)
        return progress.recalculate_progress()
    
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
