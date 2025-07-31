release: python manage.py collectstatic --noinput && python manage.py migrate
web: gunicorn video_quiz_project.wsgi:application --bind 0.0.0.0:$PORT