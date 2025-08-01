import os
import django
import psycopg2
import psycopg2.extras

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'video_quiz_project.settings')
django.setup()

from django.db import connection as sqlite_connection
from users.models import User
from videos.models import Video
from quizzes.models import Question, Answer, QuizAttempt
from django.contrib.auth.hashers import make_password
from django.utils import timezone

# PostgreSQL database connection parameters
pg_params = {
    'dbname': 'video_quiz_db',
    'user': 'postgres',
    'password': 'Admin@123',
    'host': 'localhost',
    'port': '5432'
}

def migrate_data():
    print("=== Starting data migration from PostgreSQL to SQLite ===")
    
    # Connect to PostgreSQL
    pg_conn = psycopg2.connect(**pg_params)
    pg_cursor = pg_conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    
    # Migrate users
    migrate_users(pg_cursor)
    
    # Migrate videos
    migrate_videos(pg_cursor)
    
    # Migrate questions and answers
    migrate_questions_and_answers(pg_cursor)
    
    # Migrate quiz attempts
    migrate_quiz_attempts(pg_cursor)
    
    # Close PostgreSQL connection
    pg_cursor.close()
    pg_conn.close()
    
    print("=== Data migration completed ===")

def migrate_users(pg_cursor):
    print("\n--- Migrating users ---")
    pg_cursor.execute("""
        SELECT id, username, password, email, first_name, last_name, is_staff, is_active, 
               is_superuser, date_joined, last_login, is_super_admin
        FROM core_customuser
    """)
    users = pg_cursor.fetchall()
    
    # Delete existing users in SQLite
    User.objects.all().delete()
    
    for user in users:
        try:
            User.objects.create(
                id=user['id'],
                username=user['username'],
                password=user['password'],  # Already hashed
                email=user['email'],
                first_name=user['first_name'] or '',
                last_name=user['last_name'] or '',
                is_staff=user['is_staff'],
                is_active=user['is_active'],
                is_superuser=user['is_superuser'],
                is_superadmin=user['is_super_admin'],
                date_joined=user['date_joined'],
                last_login=user['last_login'] if user['last_login'] else timezone.now()
            )
            print(f"  - Migrated user: {user['username']}")
        except Exception as e:
            print(f"  - Error migrating user {user['username']}: {e}")

def migrate_videos(pg_cursor):
    print("\n--- Migrating videos ---")
    pg_cursor.execute("""
        SELECT id, title, description, video_file, duration_minutes, 
               quiz_time_limit, passing_percentage, "order", is_active,
               created_at, updated_at
        FROM core_video
    """)
    videos = pg_cursor.fetchall()
    
    # Delete existing videos in SQLite
    Video.objects.all().delete()
    
    for video in videos:
        try:
            Video.objects.create(
                id=video['id'],
                title=video['title'],
                description=video['description'],
                video_file=video['video_file'],
                duration=video['duration_minutes'] * 60,  # Convert to seconds
                sequence_number=video['order'],
                passing_percentage=video['passing_percentage'],
                time_limit=video['quiz_time_limit'],
                is_active=video['is_active'],
                created_at=video['created_at'],
                updated_at=video['updated_at']
            )
            print(f"  - Migrated video: {video['title']}")
        except Exception as e:
            print(f"  - Error migrating video {video['title']}: {e}")

def migrate_questions_and_answers(pg_cursor):
    print("\n--- Migrating questions and answers ---")
    
    # Delete existing questions and answers in SQLite
    Question.objects.all().delete()
    Answer.objects.all().delete()
    
    # Fetch questions
    pg_cursor.execute("""
        SELECT id, question_text, "order", video_id, created_at
        FROM core_question
    """)
    questions = pg_cursor.fetchall()
    
    for question in questions:
        try:
            q = Question.objects.create(
                id=question['id'],
                video_id=question['video_id'],
                question_text=question['question_text'],
                sequence_number=question['order'],
                created_at=question['created_at'],
                updated_at=question['created_at']  # Use created_at as updated_at
            )
            
            # Fetch answers for this question
            pg_cursor.execute("""
                SELECT id, choice_text, is_correct, "order", question_id
                FROM core_choice
                WHERE question_id = %s
            """, (question['id'],))
            choices = pg_cursor.fetchall()
            
            for choice in choices:
                Answer.objects.create(
                    id=choice['id'],
                    question_id=choice['question_id'],
                    answer_text=choice['choice_text'],
                    is_correct=choice['is_correct'],
                    sequence_number=choice['order']
                )
            
            print(f"  - Migrated question ID {question['id']} with {len(choices)} answers")
        except Exception as e:
            print(f"  - Error migrating question {question['id']}: {e}")

def migrate_quiz_attempts(pg_cursor):
    print("\n--- Migrating quiz attempts ---")
    
    # Delete existing quiz attempts in SQLite
    QuizAttempt.objects.all().delete()
    
    # Fetch quiz attempts
    pg_cursor.execute("""
        SELECT id, user_id, video_id, attempt_number, start_time, end_time, 
               time_remaining, status, score, percentage, passed
        FROM core_quizattempt
    """)
    attempts = pg_cursor.fetchall()
    
    for attempt in attempts:
        try:
            QuizAttempt.objects.create(
                id=attempt['id'],
                user_id=attempt['user_id'],
                video_id=attempt['video_id'],
                attempt_number=attempt['attempt_number'],
                start_time=attempt['start_time'],
                end_time=attempt['end_time'],
                time_remaining=attempt['time_remaining'] if attempt['time_remaining'] is not None else 0,
                status=attempt['status'],
                score=attempt['score'],
                percentage=attempt['percentage'],
                is_passed=attempt['passed']
            )
            print(f"  - Migrated quiz attempt ID {attempt['id']}")
            
            # TODO: Also migrate user answers if needed
            
        except Exception as e:
            print(f"  - Error migrating quiz attempt {attempt['id']}: {e}")

if __name__ == "__main__":
    migrate_data()
