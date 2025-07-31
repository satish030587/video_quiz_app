FROM python:3.11-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy project
COPY . .

# Collect static files
RUN python manage.py collectstatic --noinput

# Run migrations during build
RUN python manage.py migrate

# Command to run when the container starts
CMD ["gunicorn", "video_quiz_project.wsgi:application", "--bind", "0.0.0.0:$PORT"]
