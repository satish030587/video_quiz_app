Final Product Requirements Document (PRD): Video-Based Quiz Application
1. Product Overview
1.1 Introduction
The Video-Based Quiz Application is an educational platform where users watch videos and answer questions based on the video content. The platform features a progressive learning path where users must successfully complete quizzes to unlock subsequent content, with anti-cheating measures to maintain integrity.

1.2 Tech Stack
Backend: Django
Frontend: React.js
Database: PostgreSQL
Styling: Tailwind CSS
Timer Integration: React Hooks with server-side validation
Anti-Cheating: Server-side session management + JWT tokens
2. User Roles and Permissions
2.1 Super Admin
Create and manage user accounts
Create, edit, and delete video content
Create, edit, and delete quiz questions and answers
Set passing percentage for quizzes (default 70%)
Set time limits for each quiz
View user statistics and progress
Generate and download certificates for qualified users
2.2 User
Login to the platform (no self-registration)
View dashboard with progress statistics
Take video quizzes with limited attempts
View results after quiz submission
Download completion certificate upon meeting requirements
3. Feature Requirements
3.1 Authentication System
3.1.1 User Management (Super Admin)
Super admin creates user accounts with:
Username
Email
Initial password
User profile details
No self-registration for users
3.1.2 Login System
Username and password login
"Remember me" functionality
Session timeout after 30 minutes of inactivity
3.1.3 Logout
Clear session data
Display logout confirmation message
Redirect to login page
3.2 Super Admin Panel
3.2.1 Content Management
Unified interface to create/edit:
Video content (upload, URL embedding, description)
Quiz questions related to video content
Multiple-choice answers with correct answer marking
Ability to set passing percentage for each quiz (default 70%)
Option to set time limit for each quiz
3.2.2 User Management
Create new user accounts
Edit existing user details
View individual user progress and statistics
3.2.3 Certificate Management
Generate certificates for users who complete all videos
Option to download certificates in PDF format
Basic certificate design with:
User's name
Achievement description
Completion date
Unique certificate ID
Digital signature or stamp
3.3 User Dashboard
3.3.1 Navigation
App logo/name prominently displayed
User profile information
Profile editing option
Logout button
3.3.2 Statistics Display
Total number of videos available
Number of videos passed
Number of videos failed
Total retries used
Overall progress percentage
Remaining attempts for each video
3.3.3 Video Listing
Grid/list view of all available videos
Clear visual indication of:
Unlocked videos
Locked videos
Completed videos
Failed videos with remaining attempts
Videos with no remaining attempts
First video unlocked by default
Subsequent videos unlock only after previous video quiz passed
3.4 Quiz Interface
3.4.1 Quiz Navigation
Navbar showing current video title
User information and logout option
Video player prominently displayed
Timer showing remaining time clearly visible
Next/Previous question navigation buttons
Question pagination with visual indicators for:
Answered questions
Unanswered questions
Current question
3.4.2 Question Display
One question displayed at a time
Multiple-choice options clearly presented
State persistence when navigating between questions
Submit button appears only when all questions are viewed
3.4.3 Timer Functionality
Countdown timer visible throughout quiz
Server-side time tracking to prevent manipulation
Automatic submission when time expires
Timer persists across page refreshes and network issues
3.5 Results System
3.5.1 Results Page
Summary statistics:
Total questions
Questions attempted
Correct answers (1 point per correct answer)
Percentage score
List of incorrect answers (without revealing correct answers)
Pass/fail status clearly indicated
Display of remaining attempts if failed
Option to return to dashboard
3.5.2 Certificate Generation
Automatic generation upon completion of all videos with passing scores
Downloadable PDF format
Unique certificate ID for verification
User name, completion date, and achievement details included
4. Business Logic
4.1 Quiz Progression Logic
Users can only access unlocked videos
First video is unlocked by default
Subsequent videos unlock only when previous video's quiz is passed
Pass/fail determined by configurable percentage threshold (default: 70%)
Maximum 2 attempts per video quiz
After 2 failed attempts, quiz is marked as "Maximum attempts reached"
4.2 Quiz Session Logic
Quiz starts when user clicks "Start Quiz" button
If quiz was interrupted, "Resume Quiz" option appears instead
Timer starts on quiz start and continues server-side
User answers are saved in real-time to server
Session maintains question state (answered/unanswered)
Quiz automatically submits when:
User clicks submit button
Timer expires (with all attempted answers recorded)
All attempts to manipulate the system are detected
4.3 Anti-Cheating Logic
Server-side session management for timer and quiz state
Timer continues running server-side despite:
Page refreshes
Browser back/forward navigation
Network disconnections
Quiz state (current question, answers) persisted server-side
Prevention of multiple logins from different devices
Session-bound tokens that expire with the timer
5. Database Models
5.1 User Model

class User(AbstractUser):
    email = models.EmailField(unique=True)
    is_superadmin = models.BooleanField(default=False)
    date_joined = models.DateTimeField(auto_now_add=True)
    last_login = models.DateTimeField(auto_now=True)
    profile_picture = models.ImageField(upload_to='profile_pics/', null=True, blank=True)
    
    class Meta:
        db_table = 'users'

5.2 Video Model

class Video(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField()
    video_file = models.FileField(upload_to='videos/', null=True, blank=True)
    video_url = models.URLField(null=True, blank=True)
    duration = models.IntegerField(help_text="Duration in seconds")
    sequence_number = models.IntegerField(help_text="Order in which videos appear")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    passing_percentage = models.IntegerField(default=70)
    time_limit = models.IntegerField(help_text="Quiz time limit in minutes")
    is_active = models.BooleanField(default=True)
    
    class Meta:
        db_table = 'videos'
        ordering = ['sequence_number']


5.3 Question Model

class Question(models.Model):
    video = models.ForeignKey(Video, on_delete=models.CASCADE, related_name='questions')
    question_text = models.TextField()
    sequence_number = models.IntegerField(help_text="Order in which questions appear")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'questions'
        ordering = ['sequence_number']

5.4 Answer Model

class Answer(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name='answers')
    answer_text = models.TextField()
    is_correct = models.BooleanField(default=False)
    sequence_number = models.IntegerField(help_text="Order in which answers appear")
    
    class Meta:
        db_table = 'answers'
        ordering = ['sequence_number']


5.5 Quiz Attempt Model


class QuizAttempt(models.Model):
    STATUS_CHOICES = (
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
        ('timed_out', 'Timed Out'),
    )
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='quiz_attempts')
    video = models.ForeignKey(Video, on_delete=models.CASCADE, related_name='attempts')
    attempt_number = models.IntegerField()
    start_time = models.DateTimeField(auto_now_add=True)
    end_time = models.DateTimeField(null=True, blank=True)
    time_remaining = models.IntegerField(help_text="Time remaining in seconds")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='in_progress')
    score = models.IntegerField(null=True, blank=True)
    percentage = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    is_passed = models.BooleanField(null=True, blank=True)
    
    class Meta:
        db_table = 'quiz_attempts'
        unique_together = ['user', 'video', 'attempt_number']


5.6 User Answer Model

class UserAnswer(models.Model):
    quiz_attempt = models.ForeignKey(QuizAttempt, on_delete=models.CASCADE, related_name='user_answers')
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    selected_answer = models.ForeignKey(Answer, on_delete=models.CASCADE, null=True, blank=True)
    is_correct = models.BooleanField(null=True, blank=True)
    
    class Meta:
        db_table = 'user_answers'
        unique_together = ['quiz_attempt', 'question']


5.7 User Progress Model

class UserProgress(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='progress')
    videos_passed = models.ManyToManyField(Video, related_name='passed_by_users', blank=True)
    videos_failed = models.ManyToManyField(Video, related_name='failed_by_users', blank=True)
    total_retries = models.IntegerField(default=0)
    overall_progress = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    last_updated = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'user_progress'


5.8 Certificate Model

class Certificate(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='certificates')
    unique_id = models.CharField(max_length=50, unique=True)
    issue_date = models.DateTimeField(auto_now_add=True)
    pdf_file = models.FileField(upload_to='certificates/', null=True, blank=True)
    is_downloaded = models.BooleanField(default=False)
    
    class Meta:
        db_table = 'certificates'


6. Implementation Guidelines
6.1 Frontend Implementation
Use React.js for component-based UI development
Implement responsive design using Tailwind CSS
Use React Context API or Redux for state management
Integrate with backend via RESTful API endpoints
6.2 Backend Implementation
Implement Django REST framework for API endpoints
Use Django's authentication system with JWT tokens
Implement proper permission checks for all views
Store session data in Redis for better performance
6.3 Server-Side Validation
All quiz actions validated server-side
JWT tokens with short expiry to validate quiz sessions
Server maintains the source of truth for:
Timer state
Question/answer state
User progress
6.4 Database Optimization
Use appropriate indexes for frequently queried fields
Implement database-level constraints for data integrity
Use Django's ORM efficiently to minimize database queries
7. MVP Development Roadmap
Phase 1: Core Authentication & Admin (2 weeks)
Super admin user management system
User login system
Basic admin panel with video and question management
Database setup and model implementation
Phase 2: Basic Quiz Functionality (3 weeks)
Video player integration
Basic quiz interface
Question navigation system
Answer submission and evaluation
Phase 3: Dashboard & Progression (2 weeks)
User dashboard with statistics
Video unlocking progression system
Attempt limitation implementation
Phase 4: Anti-Cheating & Timer (2 weeks)
Server-side timer implementation
Session persistence across refreshes
Anti-cheating measures implementation
Phase 5: Certificate & Polish (1 week)
Certificate generation system
UI/UX refinements
Final testing and optimization
8. Conclusion
This Video-Based Quiz Application provides a structured learning environment where users progress through video content and quizzes in a sequential manner. The anti-cheating measures ensure the integrity of the assessment process, while the certificate generation rewards successful completion. The implementation follows best practices for security and performance while maintaining a user-friendly interface.