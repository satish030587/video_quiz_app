class DatabaseRouter:
    """
    A router to map model table names to actual database table names.
    """
    # Table mapping between model's db_table and actual database table
    TABLE_MAP = {
        'users': 'core_customuser',
        'videos': 'core_video',
        'questions': 'core_question',
        'answers': 'core_choice',
        'quiz_attempts': 'core_quizattempt',
        'user_answers': 'core_useranswer',
        'user_progress': 'core_uservideoprogress',
        'certificates': 'core_certificate' if 'core_certificate' else None,
    }
    
    def db_for_read(self, model, **hints):
        return 'default'
        
    def db_for_write(self, model, **hints):
        return 'default'
        
    def allow_relation(self, obj1, obj2, **hints):
        return True
        
    def allow_migrate(self, db, app_label, model_name=None, **hints):
        return False  # Prevent migrations as we're using an existing database
