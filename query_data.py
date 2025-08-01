import os
import django

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'video_quiz_project.settings')
django.setup()

from django.db import connection
from users.models import User
from videos.models import Video
from quizzes.models import Question

def get_data():
    print("=== Querying PostgreSQL Database ===")
    
    # Using Django ORM with mapped tables
    try:
        print("\n--- USERS ---")
        users = User.objects.all()
        print(f"Count: {users.count()}")
        for user in users:
            print(f"User: {user.username} (ID: {user.id})")
    except Exception as e:
        print(f"Error retrieving users via ORM: {e}")
        
    try:
        print("\n--- VIDEOS ---")
        videos = Video.objects.all()
        print(f"Count: {videos.count()}")
        for video in videos[:5]:  # Show first 5 only
            print(f"Video: {video.title} (ID: {video.id})")
    except Exception as e:
        print(f"Error retrieving videos via ORM: {e}")
        
    # Using raw SQL for direct database access
    print("\n--- DIRECT SQL QUERIES ---")
    
    with connection.cursor() as cursor:
        try:
            cursor.execute("""
                SELECT id, username, email, is_staff
                FROM core_customuser
                LIMIT 5
            """)
            rows = cursor.fetchall()
            print("Users (via SQL):")
            for row in rows:
                print(f"  ID: {row[0]}, Username: {row[1]}, Email: {row[2]}")
        except Exception as e:
            print(f"Error with direct SQL - users: {e}")
            
        try:
            cursor.execute("""
                SELECT id, title, description
                FROM core_video
                LIMIT 5
            """)
            rows = cursor.fetchall()
            print("\nVideos (via SQL):")
            for row in rows:
                print(f"  ID: {row[0]}, Title: {row[1]}")
        except Exception as e:
            print(f"Error with direct SQL - videos: {e}")
            
        try:
            cursor.execute("""
                SELECT id, question_text
                FROM core_question
                LIMIT 5
            """)
            rows = cursor.fetchall()
            print("\nQuestions (via SQL):")
            for row in rows:
                print(f"  ID: {row[0]}, Question: {row[1][:50]}...")
        except Exception as e:
            print(f"Error with direct SQL - questions: {e}")

if __name__ == "__main__":
    get_data()
