from rest_framework import serializers
from .models import Question, Answer, QuizAttempt, UserAnswer

class AnswerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Answer
        fields = ['id', 'answer_text', 'sequence_number']
        # Note: is_correct is excluded to prevent cheating

class QuestionSerializer(serializers.ModelSerializer):
    answers = AnswerSerializer(many=True, read_only=True)
    
    class Meta:
        model = Question
        fields = ['id', 'question_text', 'sequence_number', 'answers']

class UserAnswerSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserAnswer
        fields = ['id', 'question', 'selected_answer']

class QuizAttemptSerializer(serializers.ModelSerializer):
    user_answers = UserAnswerSerializer(many=True, read_only=True)
    
    class Meta:
        model = QuizAttempt
        fields = [
            'id', 'user', 'video', 'attempt_number', 'start_time', 
            'end_time', 'time_remaining', 'status', 'score', 
            'percentage', 'is_passed', 'user_answers'
        ]
        read_only_fields = ['user', 'start_time', 'end_time', 'score', 'percentage', 'is_passed']

class QuizResultSerializer(serializers.ModelSerializer):
    """Serializer for quiz results without revealing correct answers"""
    total_questions = serializers.SerializerMethodField()
    questions_attempted = serializers.SerializerMethodField()
    correct_answers = serializers.SerializerMethodField()
    
    class Meta:
        model = QuizAttempt
        fields = [
            'id', 'video', 'attempt_number', 'total_questions', 
            'questions_attempted', 'correct_answers', 'score', 
            'percentage', 'is_passed', 'status'
        ]
    
    def get_total_questions(self, obj):
        return Question.objects.filter(video=obj.video).count()
    
    def get_questions_attempted(self, obj):
        return obj.user_answers.count()
    
    def get_correct_answers(self, obj):
        return obj.user_answers.filter(is_correct=True).count()

class SubmitAnswerSerializer(serializers.Serializer):
    question_id = serializers.IntegerField()
    answer_id = serializers.IntegerField()