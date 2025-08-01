import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'video_quiz_project.settings')
django.setup()

from django.contrib.auth import get_user_model
from users.models import UserProgress
from videos.models import Video
from quizzes.models import QuizAttempt, Question, Answer, UserAnswer
from django.utils import timezone

def create_test_scenario():
    """Create a test scenario to validate the progress syncing"""
    print("Creating test scenario...")
    
    User = get_user_model()
    
    # Create test user if it doesn't exist
    test_username = 'testuser'
    user, created = User.objects.get_or_create(
        username=test_username,
        defaults={
            'email': 'testuser@example.com',
            'is_active': True
        }
    )
    
    if created:
        user.set_password('testpassword')
        user.save()
        print(f"Created test user: {test_username}")
    else:
        print(f"Using existing test user: {test_username}")
    
    # Get the first video
    video = Video.objects.order_by('sequence_number').first()
    if not video:
        print("No videos found. Please create a video first.")
        return
    
    print(f"Using video: {video.title} (Sequence: {video.sequence_number})")
    
    # Create a quiz attempt
    attempt, created = QuizAttempt.objects.get_or_create(
        user=user,
        video=video,
        attempt_number=1,
        defaults={
            'time_remaining': 300,
            'status': 'completed',
            'score': video.passing_percentage + 1,  # Ensure it passes
            'percentage': float(video.passing_percentage + 1),
            'is_passed': True,
            'end_time': timezone.now()
        }
    )
    
    if not created:
        # Update existing attempt to make sure it's passed
        attempt.status = 'completed'
        attempt.score = video.passing_percentage + 1
        attempt.percentage = float(video.passing_percentage + 1)
        attempt.is_passed = True
        attempt.save()
        print(f"Updated existing quiz attempt: {attempt.id}")
    else:
        print(f"Created new quiz attempt: {attempt.id}")
    
    # Get user progress
    progress, created = UserProgress.objects.get_or_create(user=user)
    
    # Check initial state
    print("\nInitial state:")
    videos_passed = progress.videos_passed.count()
    print(f"Videos passed: {videos_passed}")
    print(f"Overall progress: {progress.overall_progress}")
    
    # Test sync_with_quiz_attempts
    print("\nSyncing with quiz attempts...")
    result = progress.sync_with_quiz_attempts()
    print(f"Sync result: {result}")
    
    # Check final state
    print("\nFinal state:")
    videos_passed = progress.videos_passed.count()
    print(f"Videos passed: {videos_passed}")
    print(f"Overall progress: {progress.overall_progress}")
    
    # Verify video is in videos_passed
    if video in progress.videos_passed.all():
        print(f"\nSuccess: Video '{video.title}' is correctly marked as passed!")
    else:
        print(f"\nError: Video '{video.title}' is NOT marked as passed!")
    
    print("\nTest completed!")

if __name__ == "__main__":
    create_test_scenario()
