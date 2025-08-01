from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from quizzes.models import QuizAttempt
from videos.models import Video
from users.models import UserProgress
from django.utils import timezone

class Command(BaseCommand):
    help = 'Tests the automatic progress update functionality'

    def handle(self, *args, **kwargs):
        self.stdout.write(self.style.SUCCESS('Testing automatic progress update...'))
        
        User = get_user_model()
        
        # Get or create test user
        test_username = 'progresstest'
        user, created = User.objects.get_or_create(
            username=test_username,
            defaults={
                'email': 'progresstest@example.com',
                'is_active': True
            }
        )
        
        if created:
            user.set_password('password123')
            user.save()
            self.stdout.write(f"Created test user: {test_username}")
        else:
            self.stdout.write(f"Using existing test user: {test_username}")
        
        # Get the first video
        video = Video.objects.order_by('sequence_number').first()
        if not video:
            self.stdout.write(self.style.ERROR("No videos found. Please create a video first."))
            return
        
        self.stdout.write(f"Using video: {video.title}")
        
        # Clear any existing progress
        progress, created = UserProgress.objects.get_or_create(user=user)
        progress.videos_passed.clear()
        progress.videos_failed.clear()
        progress.overall_progress = 0
        progress.save()
        
        self.stdout.write(self.style.SUCCESS(f"\nInitial progress: {progress.overall_progress}%"))
        self.stdout.write(f"Videos passed: {progress.videos_passed.count()}")
        
        # Create quiz attempt that passes
        self.stdout.write(self.style.SUCCESS("\nCreating passing quiz attempt..."))
        attempt = QuizAttempt.objects.create(
            user=user,
            video=video,
            attempt_number=1,
            time_remaining=300,
            status='completed',
            score=video.passing_percentage + 10,  # Ensure it passes
            percentage=float(video.passing_percentage + 10),
            is_passed=True,
            end_time=timezone.now()
        )
        
        # Check if progress was automatically updated
        progress.refresh_from_db()
        self.stdout.write(self.style.SUCCESS(f"\nProgress after passing attempt: {progress.overall_progress}%"))
        self.stdout.write(f"Videos passed: {progress.videos_passed.count()}")
        self.stdout.write(f"Videos passed includes test video: {video in progress.videos_passed.all()}")
        
        # Delete the attempt and check if progress updates
        self.stdout.write(self.style.SUCCESS("\nDeleting quiz attempt..."))
        attempt.delete()
        
        # Check if progress was automatically updated
        progress.refresh_from_db()
        self.stdout.write(self.style.SUCCESS(f"\nProgress after deleting attempt: {progress.overall_progress}%"))
        self.stdout.write(f"Videos passed: {progress.videos_passed.count()}")
        self.stdout.write(f"Videos passed includes test video: {video in progress.videos_passed.all()}")
        
        self.stdout.write(self.style.SUCCESS("\nTest completed!"))
