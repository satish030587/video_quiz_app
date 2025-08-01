from django.apps import AppConfig


class QuizzesConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'quizzes'
    
    def ready(self):
        """
        Import signals when the app is ready
        This ensures user progress is automatically updated when quiz attempts change
        """
        import quizzes.signals
