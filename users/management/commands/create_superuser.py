from django.core.management.base import BaseCommand
from users.models import User

class Command(BaseCommand):
    help = 'Creates a new superuser'

    def handle(self, *args, **options):
        if not User.objects.filter(username='adminuser').exists():
            User.objects.create_superuser(
                username='adminuser',
                email='admin@example.com',
                password='SecurePassword123!',
                is_superadmin=True
            )
            self.stdout.write(self.style.SUCCESS('Superuser created successfully'))
        else:
            self.stdout.write(self.style.SUCCESS('Superuser already exists'))
