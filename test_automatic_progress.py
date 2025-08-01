import os
import django
import traceback

print("Script starting...")
try:
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'video_quiz_project.settings')
    django.setup()
    
    print("Django setup successful")
    from django.contrib.auth import get_user_model
    print("Imports successful")
except Exception as e:
    print(f"Error during setup: {e}")
    traceback.print_exc()
from quizzes.models import QuizAttempt
from videos.models import Video
from users.models import UserProgress
from django.utils import timezone

def test_automatic_progress_update():
    """Test that user progress automatically updates when quiz attempts change"""
    print("Testing automatic progress update...")
    
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
        print(f"Created test user: {test_username}")
    else:
        print(f"Using existing test user: {test_username}")
    
    # Get the first video
    video = Video.objects.order_by('sequence_number').first()
    if not video:
        print("No videos found. Please create a video first.")
        return
    
    print(f"Using video: {video.title}")
    
    # Check initial progress
    progress, created = UserProgress.objects.get_or_create(user=user)
    print(f"\nInitial progress: {progress.overall_progress}%")
    print(f"Videos passed: {progress.videos_passed.count()}")
    
    # Create quiz attempt that passes
    print("\nCreating passing quiz attempt...")
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
    print(f"\nProgress after passing attempt: {progress.overall_progress}%")
    print(f"Videos passed: {progress.videos_passed.count()}")
    print(f"Videos passed includes test video: {video in progress.videos_passed.all()}")
    
    # Delete the attempt and check if progress updates
    print("\nDeleting quiz attempt...")
    attempt.delete()
    
    # Check if progress was automatically updated
    progress.refresh_from_db()
    print(f"\nProgress after deleting attempt: {progress.overall_progress}%")
    print(f"Videos passed: {progress.videos_passed.count()}")
    print(f"Videos passed includes test video: {video in progress.videos_passed.all()}")
    
    print("\nTest completed!")

if __name__ == "__main__":
    test_automatic_progress_update()
