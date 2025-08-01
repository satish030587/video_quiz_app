from django.test import Client
from django.contrib.auth import get_user_model
import os

# Django setup
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'video_quiz_project.settings')
django.setup()

User = get_user_model()

try:
    # Create a test client
    client = Client()
    
    # Get admin user credentials
    username = input("Enter admin username: ")
    password = input("Enter admin password: ")
    
    # Log in as admin
    login_successful = client.login(username=username, password=password)
    
    if login_successful:
        print("Login successful!")
        
        # Try to access the User Progress admin page
        response = client.get('/admin/users/userprogress/')
        
        # Check response
        print(f"Admin page status code: {response.status_code}")
        if response.status_code == 200:
            print("Success! The admin page loads correctly.")
        else:
            print(f"Error: Failed to load admin page. Status code: {response.status_code}")
    else:
        print("Login failed. Check your credentials.")
except Exception as e:
    print(f"Error: {str(e)}")
    import traceback
    traceback.print_exc()
