from django.core.management.base import BaseCommand
from django.db import connection
from users.models import User
from videos.models import Video
from quizzes.models import Question, Answer, QuizAttempt

class Command(BaseCommand):
    help = 'Display data from PostgreSQL database using model mappings'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('Retrieving data from PostgreSQL database...'))
        
        # Test User model (maps to core_customuser)
        try:
            users = User.objects.all()
            self.stdout.write(self.style.SUCCESS(f'Users: {users.count()}'))
            for user in users:
                self.stdout.write(f'  - {user.username} (ID: {user.id})')
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Error retrieving users: {e}'))
        
        # Test Video model (maps to core_video)
        try:
            videos = Video.objects.all()
            self.stdout.write(self.style.SUCCESS(f'Videos: {videos.count()}'))
            for video in videos[:5]:  # Show first 5 only
                self.stdout.write(f'  - {video.title} (ID: {video.id})')
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Error retrieving videos: {e}'))
        
        # Test Question model (maps to core_question)
        try:
            questions = Question.objects.all()
            self.stdout.write(self.style.SUCCESS(f'Questions: {questions.count()}'))
            for question in questions[:5]:  # Show first 5 only
                self.stdout.write(f'  - {question.question_text[:50]}... (ID: {question.id})')
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Error retrieving questions: {e}'))
            
        # Show raw SQL query for direct database access
        with connection.cursor() as cursor:
            cursor.execute("SELECT COUNT(*) FROM core_customuser")
            count = cursor.fetchone()[0]
            self.stdout.write(self.style.SUCCESS(f'Direct SQL - User count: {count}'))
            
            cursor.execute("SELECT COUNT(*) FROM core_video")
            count = cursor.fetchone()[0]
            self.stdout.write(self.style.SUCCESS(f'Direct SQL - Video count: {count}'))
