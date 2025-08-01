import os
import django
import sys

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'video_quiz_project.settings')
django.setup()

from django.contrib.auth import get_user_model
from videos.models import Video
from quizzes.models import Question, Answer

User = get_user_model()

def add_sample_data():
    """Add sample videos, questions, and answers to the database"""
    print("Adding sample data...")
    
    # Verify admin user exists
    try:
        admin_user = User.objects.get(username='admin')
        print(f"Found admin user: {admin_user.username}")
    except User.DoesNotExist:
        print("Admin user not found. Creating...")
        admin_user = User.objects.create_superuser(
            username='admin',
            email='admin@example.com',
            password='Admin@123'
        )
        print(f"Created admin user: {admin_user.username}")
    
    # Video topics
    video_topics = [
        "Windows 10 Installation Step by Step",
        "WordPress Installation",
        "JavaScript Basics",
        "Python Basics"
    ]
    
    # Create or get videos
    videos = []
    for i, topic in enumerate(video_topics, 1):
        video, created = Video.objects.get_or_create(
            title=topic,
            defaults={
                'description': f"A comprehensive guide to {topic}",
                'video_url': 'https://example.com/video.mp4',
                'duration': 600,  # 10 minutes
                'sequence_number': i,
                'passing_percentage': 70,
                'time_limit': 15,  # 15 minutes
                'is_active': True
            }
        )
        if created:
            print(f"Created video: {video.title}")
        else:
            print(f"Using existing video: {video.title}")
        videos.append(video)
    
    # Questions for each video
    for video in videos:
        # Clear existing questions for the video
        print(f"\nCreating questions for: {video.title}")
        Question.objects.filter(video=video).delete()
        
        if video.title == "Windows 10 Installation Step by Step":
            create_windows10_questions(video)
        elif video.title == "WordPress Installation":
            create_wordpress_questions(video)
        elif video.title == "JavaScript Basics":
            create_javascript_questions(video)
        elif video.title == "Python Basics":
            create_python_questions(video)
    
    print("\nSample data creation completed!")

def create_question(video, text, sequence, answers_data):
    """Helper to create a question and its answers"""
    question = Question.objects.create(
        video=video,
        question_text=text,
        sequence_number=sequence
    )
    print(f"  Added question: {question.question_text[:40]}...")
    
    # Create answers
    for i, (answer_text, is_correct) in enumerate(answers_data, 1):
        Answer.objects.create(
            question=question,
            answer_text=answer_text,
            is_correct=is_correct,
            sequence_number=i
        )
    return question

def create_windows10_questions(video):
    """Create Windows 10 Installation questions"""
    q1 = create_question(
        video, 
        "What is the minimum RAM requirement for Windows 10?",
        1,
        [
            ("1 GB for 32-bit or 2 GB for 64-bit", True),
            ("4 GB for both 32-bit and 64-bit", False),
            ("512 MB for 32-bit or 1 GB for 64-bit", False),
            ("8 GB for 32-bit or 16 GB for 64-bit", False)
        ]
    )
    
    q2 = create_question(
        video, 
        "Which of the following is NOT a method to install Windows 10?",
        2,
        [
            ("Using Cloud Installation", True),
            ("Using USB drive", False),
            ("Using DVD", False),
            ("Using ISO file", False)
        ]
    )
    
    q3 = create_question(
        video, 
        "What is the recommended free hard disk space for Windows 10 installation?",
        3,
        [
            ("16 GB for 32-bit or 32 GB for 64-bit", True),
            ("8 GB for 32-bit or 16 GB for 64-bit", False),
            ("32 GB for 32-bit or 64 GB for 64-bit", False),
            ("4 GB for 32-bit or 8 GB for 64-bit", False)
        ]
    )
    
    q4 = create_question(
        video, 
        "During Windows 10 installation, what information is NOT required?",
        4,
        [
            ("Credit card details", True),
            ("Language preference", False),
            ("Region setting", False),
            ("Microsoft account (optional)", False)
        ]
    )
    
    q5 = create_question(
        video, 
        "What happens when you choose 'Custom Install' during Windows 10 installation?",
        5,
        [
            ("You can format and partition your hard drive", True),
            ("It automatically preserves all your files and settings", False),
            ("It installs Windows 10 alongside your current OS", False),
            ("It downloads additional components from the internet", False)
        ]
    )
    
    q6 = create_question(
        video, 
        "Which key might you need to press to access the boot menu during Windows 10 installation?",
        6,
        [
            ("F12, F2, or Delete (depending on your computer)", True),
            ("Windows key + R", False),
            ("Ctrl + Alt + Del", False),
            ("Enter key repeatedly", False)
        ]
    )

def create_wordpress_questions(video):
    """Create WordPress Installation questions"""
    q1 = create_question(
        video, 
        "What are the minimum server requirements to install WordPress?",
        1,
        [
            ("PHP 7.4 or greater and MySQL 5.7 or MariaDB 10.3 or greater", True),
            ("PHP 5.6 and any SQL database", False),
            ("Node.js and MongoDB", False),
            ("Apache server only", False)
        ]
    )
    
    q2 = create_question(
        video, 
        "Which file is created during WordPress installation to store database connection information?",
        2,
        [
            ("wp-config.php", True),
            ("wp-settings.php", False),
            ("wp-admin.php", False),
            ("wordpress-db.php", False)
        ]
    )
    
    q3 = create_question(
        video, 
        "What information is NOT needed during the WordPress installation process?",
        3,
        [
            ("FTP credentials", True),
            ("Database name", False),
            ("Database username and password", False),
            ("Site title", False)
        ]
    )
    
    q4 = create_question(
        video, 
        "What is the 'famous 5-minute installation' in WordPress?",
        4,
        [
            ("The manual installation process through the web interface", True),
            ("Using a specialized WordPress installer tool", False),
            ("Installing WordPress via command line", False),
            ("Setting up WordPress with Docker", False)
        ]
    )
    
    q5 = create_question(
        video, 
        "After installation, where can you log in to the WordPress admin dashboard?",
        5,
        [
            ("/wp-admin or /wp-login.php", True),
            ("/admin or /dashboard", False),
            ("/wordpress/admin", False),
            ("/cms/login", False)
        ]
    )
    
    q6 = create_question(
        video, 
        "What is the default table prefix for WordPress database tables?",
        6,
        [
            ("wp_", True),
            ("wordpress_", False),
            ("wpress_", False),
            ("db_", False)
        ]
    )

def create_javascript_questions(video):
    """Create JavaScript Basics questions"""
    q1 = create_question(
        video, 
        "What is the correct way to declare a JavaScript variable?",
        1,
        [
            ("let x = 5;", True),
            ("variable x = 5;", False),
            ("x := 5;", False),
            ("def x = 5;", False)
        ]
    )
    
    q2 = create_question(
        video, 
        "Which of the following is a JavaScript data type?",
        2,
        [
            ("Symbol", True),
            ("Integer", False),
            ("Float", False),
            ("Dictionary", False)
        ]
    )
    
    q3 = create_question(
        video, 
        "How do you create a function in JavaScript?",
        3,
        [
            ("function myFunction() {}", True),
            ("def myFunction() {}", False),
            ("create function myFunction() {}", False),
            ("function:myFunction() {}", False)
        ]
    )
    
    q4 = create_question(
        video, 
        "How do you add a comment in JavaScript?",
        4,
        [
            ("// This is a comment", True),
            ("# This is a comment", False),
            ("/* This is a comment", False),
            ("-- This is a comment", False)
        ]
    )
    
    q5 = create_question(
        video, 
        "Which operator is used to assign a value to a variable in JavaScript?",
        5,
        [
            ("=", True),
            (":=", False),
            ("->", False),
            ("==", False)
        ]
    )
    
    q6 = create_question(
        video, 
        "What is the correct way to write an array in JavaScript?",
        6,
        [
            ("const cars = ['Saab', 'Volvo', 'BMW'];", True),
            ("const cars = {'Saab', 'Volvo', 'BMW'};", False),
            ("const cars = ('Saab', 'Volvo', 'BMW');", False),
            ("const cars = 'Saab', 'Volvo', 'BMW';", False)
        ]
    )

def create_python_questions(video):
    """Create Python Basics questions"""
    q1 = create_question(
        video, 
        "What is the correct way to create a variable in Python?",
        1,
        [
            ("x = 5", True),
            ("var x = 5", False),
            ("let x = 5", False),
            ("x := 5", False)
        ]
    )
    
    q2 = create_question(
        video, 
        "Which of the following is NOT a Python data type?",
        2,
        [
            ("varchar", True),
            ("list", False),
            ("tuple", False),
            ("dictionary", False)
        ]
    )
    
    q3 = create_question(
        video, 
        "How do you create a function in Python?",
        3,
        [
            ("def my_function():", True),
            ("function my_function():", False),
            ("create my_function():", False),
            ("func my_function():", False)
        ]
    )
    
    q4 = create_question(
        video, 
        "How do you add a comment in Python?",
        4,
        [
            ("# This is a comment", True),
            ("// This is a comment", False),
            ("/* This is a comment */", False),
            ("-- This is a comment", False)
        ]
    )
    
    q5 = create_question(
        video, 
        "How do you create a list in Python?",
        5,
        [
            ("my_list = ['apple', 'banana', 'cherry']", True),
            ("my_list = ('apple', 'banana', 'cherry')", False),
            ("my_list = {'apple', 'banana', 'cherry'}", False),
            ("my_list = <'apple', 'banana', 'cherry'>", False)
        ]
    )
    
    q6 = create_question(
        video, 
        "Which of these is the correct way to import a module in Python?",
        6,
        [
            ("import numpy", True),
            ("include numpy", False),
            ("using numpy", False),
            ("require numpy", False)
        ]
    )

if __name__ == "__main__":
    add_sample_data()
