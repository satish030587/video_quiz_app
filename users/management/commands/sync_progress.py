from django.core.management.base import BaseCommand
from users.models import UserProgress
from django.contrib.auth import get_user_model

class Command(BaseCommand):
    help = 'Synchronize all users progress with quiz attempts'

    def handle(self, *args, **options):
        User = get_user_model()
        users = User.objects.all()
        total_users = users.count()
        
        self.stdout.write(self.style.SUCCESS(f'Starting progress synchronization for {total_users} users...'))
        
        updated_count = 0
        for user in users:
            progress, created = UserProgress.objects.get_or_create(user=user)
            
            self.stdout.write(f'Processing user: {user.username}')
            
            # Get initial state
            initial_passed = progress.videos_passed.count()
            initial_progress = progress.overall_progress
            
            # Sync with quiz attempts
            result = progress.sync_with_quiz_attempts()
            
            # Get final state
            final_passed = progress.videos_passed.count()
            final_progress = progress.overall_progress
            
            if final_passed != initial_passed or final_progress != initial_progress:
                self.stdout.write(self.style.WARNING(
                    f'  Updated: {initial_passed} → {final_passed} videos passed, '
                    f'{initial_progress}% → {final_progress}% progress'
                ))
                updated_count += 1
            else:
                self.stdout.write(self.style.SUCCESS(f'  No changes needed'))
        
        self.stdout.write(self.style.SUCCESS(
            f'Progress synchronization completed! Updated {updated_count} out of {total_users} users.'
        ))
