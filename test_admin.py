import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'video_quiz_project.settings')
django.setup()

from users.admin import UserProgressAdmin
from users.models import UserProgress, User
from django.test import RequestFactory
from django.contrib import admin

# Create test objects
print("Setting up test objects...")
request_factory = RequestFactory()
admin_instance = UserProgressAdmin(UserProgress, admin.site)

# Get a user progress object
try:
    user_progress = UserProgress.objects.first()
    if not user_progress:
        print("No UserProgress objects found. Creating one...")
        user = User.objects.first()
        if not user:
            print("No users found. Cannot continue testing.")
            exit(1)
        user_progress = UserProgress.objects.create(user=user)
    
    print(f"Testing with UserProgress for user: {user_progress.user.username}")
    
    # Test all display methods
    print("\nTesting display_overall_progress...")
    result = admin_instance.display_overall_progress(user_progress)
    print(f"Result: {result}")
    
    print("\nTesting display_videos_passed...")
    result = admin_instance.display_videos_passed(user_progress)
    print(f"Result: {result}")
    
    print("\nTesting display_videos_passed_list...")
    result = admin_instance.display_videos_passed_list(user_progress)
    print(f"Result: {result}")
    
    print("\nTesting display_videos_failed_list...")
    result = admin_instance.display_videos_failed_list(user_progress)
    print(f"Result: {result}")
    
    print("\nTesting actions_buttons...")
    result = admin_instance.actions_buttons(user_progress)
    print(f"Result: {result}")
    
    print("\nAll tests completed successfully!")
    
except Exception as e:
    print(f"Error during testing: {str(e)}")
    import traceback
    traceback.print_exc()
