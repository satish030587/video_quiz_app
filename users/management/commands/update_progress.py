from django.core.management.base import BaseCommand
from users.models import UserProgress


class Command(BaseCommand):
    help = 'Recalculate user progress for all users'

    def add_arguments(self, parser):
        parser.add_argument(
            '--user',
            type=str,
            help='Recalculate progress for a specific user (username)',
        )
        parser.add_argument(
            '--reset',
            action='store_true',
            help='Reset progress instead of recalculating',
        )

    def handle(self, *args, **options):
        if options['user']:
            # Handle specific user
            try:
                from users.models import User
                user = User.objects.get(username=options['user'])
                progress, created = UserProgress.objects.get_or_create(user=user)
                
                if options['reset']:
                    progress.reset_progress()
                    self.stdout.write(
                        self.style.SUCCESS(f'Successfully reset progress for user: {user.username}')
                    )
                else:
                    result = progress.recalculate_progress()
                    self.stdout.write(
                        self.style.SUCCESS(f'Successfully recalculated progress for user: {user.username}')
                    )
                    self.stdout.write(f'  - Passed videos: {result["passed_videos"]}')
                    self.stdout.write(f'  - Failed videos: {result["failed_videos"]}')
                    self.stdout.write(f'  - Total retries: {result["total_retries"]}')
                    self.stdout.write(f'  - Overall progress: {result["overall_progress"]:.1f}%')
                    
            except User.DoesNotExist:
                self.stdout.write(
                    self.style.ERROR(f'User "{options["user"]}" does not exist')
                )
        else:
            # Handle all users
            if options['reset']:
                # Reset all users
                reset_count = 0
                for progress in UserProgress.objects.all():
                    progress.reset_progress()
                    reset_count += 1
                self.stdout.write(
                    self.style.SUCCESS(f'Successfully reset progress for {reset_count} users')
                )
            else:
                # Recalculate all users
                updated_count = UserProgress.recalculate_all_progress()
                self.stdout.write(
                    self.style.SUCCESS(f'Successfully recalculated progress for {updated_count} users')
                )
