import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'video_quiz_project.settings')
django.setup()

from users.models import UserProgress, User
from videos.models import Video
from quizzes.models import QuizAttempt
from django.utils import timezone

def test_user_progress_update():
    print("Testing user progress update...")
    
    # Get a user or create one
    user = User.objects.first()
    if not user:
        print("No users found. Cannot test.")
        return
    
    # Get a video or create one
    video = Video.objects.first()
    if not video:
        print("No videos found. Cannot test.")
        return
    
    # Get or create user progress
    progress, created = UserProgress.objects.get_or_create(user=user)
    
    # Initial state
    initial_passed = progress.videos_passed.count()
    initial_progress = float(progress.overall_progress)
    print(f"Initial state: {initial_passed} videos passed, {initial_progress:.2f}% overall progress")
    
    # Simulate passing a quiz
    print(f"Simulating quiz pass for video: {video.title}")
    
    # Create a quiz attempt and mark as passed
    attempt, created = QuizAttempt.objects.get_or_create(
        user=user,
        video=video,
        defaults={
            'attempt_number': 1,
            'time_remaining': 600,
            'status': 'completed',
            'score': 100,
            'percentage': 100.0,
            'is_passed': True,
            'end_time': timezone.now()
        }
    )
    
    if not created:
        attempt.is_passed = True
        attempt.percentage = 100.0
        attempt.status = 'completed'
        attempt.save()
    
    # Add the video to passed videos and recalculate progress
    progress.videos_passed.add(video)
    if video in progress.videos_failed.all():
        progress.videos_failed.remove(video)
    
    # Call recalculate_progress
    print("Calling recalculate_progress()...")
    result = progress.recalculate_progress()
    
    # Check the updated state
    updated_passed = progress.videos_passed.count()
    updated_progress = float(progress.overall_progress)
    print(f"Updated state: {updated_passed} videos passed, {updated_progress:.2f}% overall progress")
    
    # Reload from database to verify persistence
    progress = UserProgress.objects.get(id=progress.id)
    db_passed = progress.videos_passed.count()
    db_progress = float(progress.overall_progress)
    print(f"From database: {db_passed} videos passed, {db_progress:.2f}% overall progress")
    
    print("Test completed!")

if __name__ == "__main__":
    test_user_progress_update()
