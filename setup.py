#!/usr/bin/env python
import os
import django
from django.core.management import execute_from_command_line

if __name__ == "__main__":
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "video_quiz_project.settings")
    django.setup()
    
    # Collect static files
    print("Collecting static files...")
    execute_from_command_line(['manage.py', 'collectstatic', '--noinput'])
    
    # Create superuser
    print("Creating superuser...")
    execute_from_command_line(['manage.py', 'create_superuser'])
    
    print("Setup complete!")
