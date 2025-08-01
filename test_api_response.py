import os
import django
import json

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'video_quiz_project.settings')
django.setup()

from django.test import RequestFactory, Client
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from users.views import UserProgressViewSet
from users.models import UserProgress, User
from videos.models import Video
from quizzes.models import QuizAttempt

def test_api_response():
    print("Testing API response for user progress...")
    
    # Get a user or create one
    User = get_user_model()
    user = User.objects.filter(username='rakesh').first()
    
    if not user:
        print("User 'rakesh' not found. Please make sure this user exists.")
        return
    
    # Print user info
    print(f"Testing with user: {user.username} (ID: {user.id})")
    
    # Check if user has UserProgress
    try:
        progress = UserProgress.objects.get(user=user)
        print(f"UserProgress found with ID: {progress.id}")
    except UserProgress.DoesNotExist:
        print("UserProgress not found for this user. Creating one...")
        progress = UserProgress.objects.create(user=user)
        print(f"Created UserProgress with ID: {progress.id}")
    
    # Check videos passed
    passed_videos = progress.videos_passed.all()
    print(f"User has passed {passed_videos.count()} videos:")
    for video in passed_videos:
        print(f"- {video.title} (ID: {video.id})")
    
    # Check overall progress
    print(f"Current overall_progress value: {progress.overall_progress}")
    
    # Test recalculate_progress method
    print("Testing recalculate_progress method...")
    result = progress.recalculate_progress()
    print(f"After recalculation: {result}")
    
    # Check if the progress was saved to the database
    progress_from_db = UserProgress.objects.get(id=progress.id)
    print(f"From database after recalculation: {progress_from_db.overall_progress}")
    
    # Setup test client for API testing
    client = APIClient()
    client.force_authenticate(user=user)
    
    # Test the my_progress endpoint
    print("\nTesting my_progress API endpoint...")
    response = client.get('/api/auth/progress/my_progress/')
    print(f"API response status code: {response.status_code}")
    print(f"API response data: {json.dumps(response.data, indent=2)}")
    
    # Compare with model data
    print("\nComparing API response with model data:")
    print(f"Model overall_progress: {progress_from_db.overall_progress}")
    print(f"API overall_progress: {response.data.get('overall_progress', 'Not found')}")
    print(f"Model videos_passed count: {progress_from_db.videos_passed.count()}")
    print(f"API videos_passed count: {len(response.data.get('videos_passed', []))}")
    
    print("\nTest completed!")

if __name__ == "__main__":
    test_api_response()
