import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'video_quiz_project.settings')
django.setup()

from users.admin import UserProgressAdmin
from users.models import UserProgress, User
from django.contrib import admin
from django.utils.html import format_html

# Test all UserProgressAdmin methods directly
class TestUserProgressAdmin:
    def run_tests(self):
        print("Testing UserProgressAdmin methods...")
        admin_instance = UserProgressAdmin(UserProgress, admin.site)
        
        # Get a user progress object or create one
        user_progress = UserProgress.objects.first()
        if not user_progress:
            print("Creating test progress record")
            user = User.objects.first()
            if not user:
                print("No users found. Cannot test.")
                return
            user_progress = UserProgress.objects.create(user=user)
        
        # Test display_overall_progress
        print("\nTesting display_overall_progress...")
        try:
            result = admin_instance.display_overall_progress(user_progress)
            print(f"Success! Result: {result}")
        except Exception as e:
            print(f"Error: {str(e)}")
            import traceback
            traceback.print_exc()
            
        # Test display_videos_passed
        print("\nTesting display_videos_passed...")
        try:
            result = admin_instance.display_videos_passed(user_progress)
            print(f"Success! Result: {result}")
        except Exception as e:
            print(f"Error: {str(e)}")
            import traceback
            traceback.print_exc()
            
        # Test display_videos_passed_list
        print("\nTesting display_videos_passed_list...")
        try:
            result = admin_instance.display_videos_passed_list(user_progress)
            print(f"Success! Result: {result}")
        except Exception as e:
            print(f"Error: {str(e)}")
            import traceback
            traceback.print_exc()
            
        # Test display_videos_failed_list
        print("\nTesting display_videos_failed_list...")
        try:
            result = admin_instance.display_videos_failed_list(user_progress)
            print(f"Success! Result: {result}")
        except Exception as e:
            print(f"Error: {str(e)}")
            import traceback
            traceback.print_exc()
            
        # Test actions_buttons
        print("\nTesting actions_buttons...")
        try:
            result = admin_instance.actions_buttons(user_progress)
            print(f"Success! Result: {result}")
        except Exception as e:
            print(f"Error: {str(e)}")
            import traceback
            traceback.print_exc()
            
        print("\nAll tests completed!")

if __name__ == "__main__":
    tester = TestUserProgressAdmin()
    tester.run_tests()
