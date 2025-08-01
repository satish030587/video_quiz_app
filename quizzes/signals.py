# In quizzes/signals.py

from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from .models import QuizAttempt
from users.models import UserProgress

@receiver(post_save, sender=QuizAttempt)
def update_progress_on_attempt_save(sender, instance, created, **kwargs):
    """
    Update user progress whenever a quiz attempt is saved
    This ensures user progress is always in sync with their quiz attempts
    """
    try:
        # Get or create user progress
        progress, created = UserProgress.objects.get_or_create(user=instance.user)
        
        # Sync with all quiz attempts
        progress.sync_with_quiz_attempts()
    except Exception as e:
        print(f"Error updating progress after quiz attempt save: {str(e)}")

@receiver(post_delete, sender=QuizAttempt)
def update_progress_on_attempt_delete(sender, instance, **kwargs):
    """
    Update user progress whenever a quiz attempt is deleted
    This ensures user progress is always in sync with their quiz attempts
    """
    try:
        # Get user progress if it exists
        try:
            progress = UserProgress.objects.get(user=instance.user)
            
            # Sync with all quiz attempts
            progress.sync_with_quiz_attempts()
        except UserProgress.DoesNotExist:
            pass  # No progress to update if it doesn't exist
    except Exception as e:
        print(f"Error updating progress after quiz attempt delete: {str(e)}")
