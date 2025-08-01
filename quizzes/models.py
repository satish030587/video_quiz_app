from django.db import models
from django.conf import settings
from videos.models import Video

class Question(models.Model):
    video = models.ForeignKey(Video, on_delete=models.CASCADE, related_name='questions')
    question_text = models.TextField()
    sequence_number = models.IntegerField(help_text="Order in which questions appear")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'questions'
        ordering = ['sequence_number']
        
    def __str__(self):
        return f"{self.video.title} - Q{self.sequence_number}: {self.question_text[:30]}..."

class Answer(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name='answers')
    answer_text = models.TextField()
    is_correct = models.BooleanField(default=False)
    sequence_number = models.IntegerField(help_text="Order in which answers appear")
    
    class Meta:
        db_table = 'answers'
        ordering = ['sequence_number']
        
    def __str__(self):
        return f"{self.answer_text[:30]}... ({'Correct' if self.is_correct else 'Incorrect'})"
    

class QuizAttempt(models.Model):
    STATUS_CHOICES = (
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
        ('timed_out', 'Timed Out'),
    )
    
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='quiz_attempts')
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
        
    def __str__(self):
        return f"{self.user.username} - {self.video.title} - Attempt {self.attempt_number}"
        
    def save(self, *args, **kwargs):
        """Override save to automatically update user progress when attempt status changes"""
        # Save the attempt first
        super().save(*args, **kwargs)
        
        # Only update progress if status is completed (quiz is finished)
        if self.status == 'completed':
            from users.models import UserProgress
            progress, created = UserProgress.objects.get_or_create(user=self.user)
            
            # If passed, add to videos_passed and remove from videos_failed
            if self.is_passed:
                progress.videos_passed.add(self.video)
                if self.video in progress.videos_failed.all():
                    progress.videos_failed.remove(self.video)
            # If failed on second attempt, add to videos_failed
            elif self.attempt_number >= 2:
                progress.videos_failed.add(self.video)
                
            # Always sync with all quiz attempts to ensure consistency
            progress.sync_with_quiz_attempts()

class UserAnswer(models.Model):
    quiz_attempt = models.ForeignKey(QuizAttempt, on_delete=models.CASCADE, related_name='user_answers')
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    selected_answer = models.ForeignKey(Answer, on_delete=models.CASCADE, null=True, blank=True)
    is_correct = models.BooleanField(null=True, blank=True)
    
    class Meta:
        db_table = 'user_answers'
        unique_together = ['quiz_attempt', 'question']
        
    def __str__(self):
        return f"{self.quiz_attempt} - {self.question}"