import sqlite3

conn = sqlite3.connect('db.sqlite3')
cursor = conn.cursor()

# Get table names
cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
tables = cursor.fetchall()
print("Tables in database:", [table[0] for table in tables])

# Users
print("\n== USERS ==")
try:
    cursor.execute('SELECT id, username, email, is_staff, is_superuser FROM users')
    for row in cursor.fetchall():
        print(row)
except sqlite3.OperationalError as e:
    print(f"Error retrieving users: {e}")

# Videos
print("\n== VIDEOS ==")
try:
    cursor.execute('SELECT id, title, description, video_file FROM videos')
    for row in cursor.fetchall():
        print(row)
except sqlite3.OperationalError as e:
    print(f"Error retrieving videos: {e}")

# Questions
print("\n== QUESTIONS ==")
try:
    cursor.execute('SELECT id, question_text, video_id FROM questions')
    for row in cursor.fetchall():
        print(row)
except sqlite3.OperationalError as e:
    print(f"Error retrieving questions: {e}")

# Answers
print("\n== ANSWERS ==")
try:
    cursor.execute('SELECT id, answer_text, is_correct, question_id FROM answers')
    for row in cursor.fetchall():
        print(row)
except sqlite3.OperationalError as e:
    print(f"Error retrieving answers: {e}")

# Quiz attempts
print("\n== QUIZ ATTEMPTS ==")
try:
    cursor.execute('SELECT id, user_id, video_id, score, start_time, end_time FROM quiz_attempts')
    for row in cursor.fetchall():
        print(row)
except sqlite3.OperationalError as e:
    print(f"Error retrieving quiz attempts: {e}")

conn.close()
