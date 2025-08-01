import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'video_quiz_project.settings')
django.setup()

from users.models import UserProgress, User
from videos.models import Video

def test_add_passed_video():
    print("Testing adding a passed video and recalculating progress...")
    
    # Get a user progress object
    user_progress = UserProgress.objects.first()
    if not user_progress:
        print("Creating test progress record")
        user = User.objects.first()
        if not user:
            print("No users found. Cannot test.")
            return
        user_progress = UserProgress.objects.create(user=user)
    
    # Get a video
    video = Video.objects.filter(is_active=True).first()
    if not video:
        print("No active videos found. Cannot test.")
        return
    
    # Add the video to passed videos
    print(f"Before: {user_progress.videos_passed.count()} videos passed, Overall progress: {user_progress.overall_progress}%")
    
    # Check if already in passed videos
    if video in user_progress.videos_passed.all():
        print(f"Video '{video.title}' already in passed videos.")
    else:
        user_progress.videos_passed.add(video)
        print(f"Added video '{video.title}' to passed videos.")
    
    # Recalculate progress
    result = user_progress.recalculate_progress()
    
    print(f"After recalculation: {result['videos_passed']} videos passed, Overall progress: {result['overall_progress']}%")
    print("Test completed!")

if __name__ == "__main__":
    test_add_passed_video()
