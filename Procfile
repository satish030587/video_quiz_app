release: python manage.py migrate && python manage.py collectstatic --noinput && python manage.py create_superuser
web: gunicorn video_quiz_project.wsgi:application --bind 0.0.0.0:$PORT