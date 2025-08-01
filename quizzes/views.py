from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.utils import timezone
from django.db import transaction
from django.shortcuts import get_object_or_404
from .models import Question, Answer, QuizAttempt, UserAnswer
from .serializers import (
    QuestionSerializer, AnswerSerializer, QuizAttemptSerializer, 
    UserAnswerSerializer, QuizResultSerializer, SubmitAnswerSerializer
)
from videos.models import Video
from users.models import UserProgress
from users.views import IsSuperAdmin

class QuestionViewSet(viewsets.ModelViewSet):
    """
    API endpoint for questions
    """
    queryset = Question.objects.all()
    serializer_class = QuestionSerializer
    
    def get_permissions(self):
        """
        Only superadmins can create, update, or delete questions
        """
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            permission_classes = [IsSuperAdmin]
        else:
            permission_classes = [permissions.IsAuthenticated]
        return [permission() for permission in permission_classes]
    
    @action(detail=False, methods=['get'])
    def by_video(self, request):
        """Get questions for a specific video"""
        video_id = request.query_params.get('video_id', None)
        if video_id:
            questions = Question.objects.filter(video_id=video_id).order_by('sequence_number')
            serializer = self.get_serializer(questions, many=True)
            return Response(serializer.data)
        return Response(
            {"detail": "Video ID is required."}, 
            status=status.HTTP_400_BAD_REQUEST
        )

class QuizAttemptViewSet(viewsets.ModelViewSet):
    """
    API endpoint for quiz attempts
    """
    serializer_class = QuizAttemptSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        if self.request.user.is_superadmin:
            return QuizAttempt.objects.all()
        return QuizAttempt.objects.filter(user=self.request.user)
    
    @transaction.atomic
    @action(detail=False, methods=['post'])
    def start(self, request):
        """Start a new quiz attempt"""
        print(f"Start quiz attempt called with data: {request.data}")
        
        video_id = request.data.get('video_id')
        if not video_id:
            print("No video_id provided in request")
            return Response(
                {"detail": "Video ID is required."}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        print(f"Attempting to start quiz for video_id: {video_id}")
        
        try:
            video = get_object_or_404(Video, pk=video_id)
            print(f"Found video: {video.title}")
        except Exception as e:
            print(f"Error finding video: {e}")
            return Response(
                {"detail": "Video not found."}, 
                status=status.HTTP_404_NOT_FOUND
            )
        
        user = request.user
        print(f"User: {user.username}")
        
        # Check if user already has an in-progress attempt
        in_progress = QuizAttempt.objects.filter(user=user, video=video, status='in_progress').first()
        if in_progress:
            print(f"Found in-progress attempt: {in_progress.id}")
            serializer = self.get_serializer(in_progress)
            return Response(serializer.data)
        
        # Check attempt count
        attempt_count = QuizAttempt.objects.filter(user=user, video=video).count()
        print(f"Current attempt count: {attempt_count}")
        
        if attempt_count >= 2:
            print("Maximum attempts reached")
            return Response(
                {"detail": "Maximum attempts reached."}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            # Create new attempt
            attempt = QuizAttempt.objects.create(
                user=user,
                video=video,
                attempt_number=attempt_count + 1,
                time_remaining=video.time_limit * 60  # Convert minutes to seconds
            )
            print(f"Created new attempt: {attempt.id}")
            
            # Create empty user answers for all questions
            questions = Question.objects.filter(video=video)
            print(f"Found {questions.count()} questions for video")
            
            for question in questions:
                UserAnswer.objects.create(quiz_attempt=attempt, question=question)
            
            print("Created user answers for all questions")
            
            serializer = self.get_serializer(attempt)
            print(f"Returning serialized data: {serializer.data}")
            return Response(serializer.data)
            
        except Exception as e:
            print(f"Error creating quiz attempt: {e}")
            return Response(
                {"detail": f"Error creating quiz attempt: {str(e)}"}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @transaction.atomic
    @action(detail=True, methods=['post'])
    def submit_answer(self, request, pk=None):
        """Submit an answer for a question"""
        attempt = self.get_object()
        
        # Check if attempt belongs to current user
        if attempt.user != request.user:
            return Response(
                {"detail": "You don't have permission to submit answers for this attempt."}, 
                status=status.HTTP_403_FORBIDDEN
            )
        
        # Check if the quiz is still in progress
        if attempt.status != 'in_progress':
            return Response(
                {"detail": f"Cannot submit answers for a {attempt.status} quiz."}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        serializer = SubmitAnswerSerializer(data=request.data)
        if serializer.is_valid():
            question_id = serializer.validated_data['question_id']
            answer_id = serializer.validated_data['answer_id']
            
            # Verify question belongs to the video
            question = get_object_or_404(Question, pk=question_id, video=attempt.video)
            
            # Verify answer belongs to the question
            answer = get_object_or_404(Answer, pk=answer_id, question=question)
            
            # Update or create user answer
            user_answer, created = UserAnswer.objects.update_or_create(
                quiz_attempt=attempt,
                question=question,
                defaults={
                    'selected_answer': answer,
                    'is_correct': answer.is_correct
                }
            )
            
            return Response({
                "detail": "Answer submitted successfully.",
                "is_correct": user_answer.is_correct
            })
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @transaction.atomic
    @action(detail=True, methods=['post'])
    def finish(self, request, pk=None):
        """Finish a quiz attempt and calculate results"""
        attempt = self.get_object()
        
        # Check if attempt belongs to current user
        if attempt.user != request.user:
            return Response(
                {"detail": "You don't have permission to finish this attempt."}, 
                status=status.HTTP_403_FORBIDDEN
            )
        
        # Check if the quiz is still in progress
        if attempt.status != 'in_progress':
            return Response(
                {"detail": f"Cannot finish a {attempt.status} quiz."}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Calculate score
        total_questions = Question.objects.filter(video=attempt.video).count()
        answered_questions = UserAnswer.objects.filter(
            quiz_attempt=attempt, 
            selected_answer__isnull=False
        ).count()
        correct_answers = UserAnswer.objects.filter(
            quiz_attempt=attempt, 
            is_correct=True
        ).count()
        
        # Update attempt
        attempt.end_time = timezone.now()
        attempt.score = correct_answers
        
        # Calculate percentage correctly using float division
        if total_questions > 0:
            # Force float division to avoid integer division giving 0
            attempt.percentage = float(correct_answers) / float(total_questions) * 100.0
            print(f"Quiz percentage calculation: {correct_answers} correct / {total_questions} total = {attempt.percentage}%")
        else:
            attempt.percentage = 0.0
            
        attempt.is_passed = attempt.percentage >= attempt.video.passing_percentage
        attempt.status = 'completed'
        attempt.save()
        
        # Update user progress if passed
        if attempt.is_passed:
            progress, created = UserProgress.objects.get_or_create(user=request.user)
            progress.videos_passed.add(attempt.video)
            if attempt.video in progress.videos_failed.all():
                progress.videos_failed.remove(attempt.video)
            progress.total_retries = QuizAttempt.objects.filter(
                user=request.user, 
                attempt_number__gt=1
            ).count()
            
            # Use sync_with_quiz_attempts to ensure complete consistency
            progress.sync_with_quiz_attempts()
        else:
            # If failed and this is the second attempt, mark as failed in progress
            if attempt.attempt_number >= 2:
                progress, created = UserProgress.objects.get_or_create(user=request.user)
                progress.videos_failed.add(attempt.video)
                # Use sync_with_quiz_attempts to ensure complete consistency
                progress.sync_with_quiz_attempts()
                progress.save()
        
        # Return quiz results
        serializer = QuizResultSerializer(attempt)
        return Response(serializer.data)
    
    @action(detail=True, methods=['get'])
    def user_answers(self, request, pk=None):
        """Get all answers submitted by the user for this attempt"""
        attempt = self.get_object()
        
        # Check if attempt belongs to current user or is superadmin
        if attempt.user != request.user and not request.user.is_superadmin:
            return Response(
                {"detail": "You don't have permission to view answers for this attempt."}, 
                status=status.HTTP_403_FORBIDDEN
            )
        
        user_answers = UserAnswer.objects.filter(quiz_attempt=attempt)
        serializer = UserAnswerSerializer(user_answers, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['get'])
    def result(self, request, pk=None):
        """Get the result of a quiz attempt"""
        attempt = self.get_object()
        
        # Check if attempt belongs to current user or is superadmin
        if attempt.user != request.user and not request.user.is_superadmin:
            return Response(
                {"detail": "You don't have permission to view this attempt."}, 
                status=status.HTTP_403_FORBIDDEN
            )
        
        serializer = QuizResultSerializer(attempt)
        return Response(serializer.data)
    
    @action(detail=True, methods=['put'])
    def update_timer(self, request, pk=None):
        """Update the remaining time for a quiz attempt"""
        attempt = self.get_object()
        
        # Check if attempt belongs to current user
        if attempt.user != request.user:
            return Response(
                {"detail": "You don't have permission to update this attempt."}, 
                status=status.HTTP_403_FORBIDDEN
            )
        
        # Check if the quiz is still in progress
        if attempt.status != 'in_progress':
            return Response(
                {"detail": f"Cannot update timer for a {attempt.status} quiz."}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        time_remaining = request.data.get('time_remaining')
        if time_remaining is None:
            return Response(
                {"detail": "Time remaining is required."}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Update time remaining
        attempt.time_remaining = time_remaining
        
        # If time has run out, finish the quiz
        if time_remaining <= 0:
            attempt.status = 'timed_out'
            attempt.end_time = timezone.now()
            
            # Calculate score
            total_questions = Question.objects.filter(video=attempt.video).count()
            correct_answers = UserAnswer.objects.filter(
                quiz_attempt=attempt, 
                is_correct=True
            ).count()
            
            attempt.score = correct_answers
            # Force float division to avoid integer division
            attempt.percentage = float(correct_answers) / float(total_questions) * 100.0 if total_questions > 0 else 0.0
            print(f"Timed-out quiz percentage: {correct_answers} correct / {total_questions} total = {attempt.percentage}%")
            attempt.is_passed = attempt.percentage >= attempt.video.passing_percentage
        
        attempt.save()
        serializer = self.get_serializer(attempt)
        return Response(serializer.data)