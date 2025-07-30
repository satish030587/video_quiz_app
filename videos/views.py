from rest_framework import viewsets, permissions, status
from rest_framework.response import Response
from rest_framework.decorators import action
from .models import Video
from .serializers import VideoSerializer, VideoListSerializer
from users.views import IsSuperAdmin
from quizzes.models import QuizAttempt
from django.http import FileResponse, HttpResponse
import os
from django.conf import settings
import mimetypes

class VideoViewSet(viewsets.ModelViewSet):
    """
    API endpoint for videos
    """
    queryset = Video.objects.all().order_by('sequence_number')
    
    def get_permissions(self):
        """
        Only superadmins can create, update, or delete videos
        """
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            permission_classes = [IsSuperAdmin]
        else:
            permission_classes = [permissions.IsAuthenticated]
        return [permission() for permission in permission_classes]
    
    def get_serializer_class(self):
        if self.action == 'list':
            return VideoListSerializer
        return VideoSerializer
    
    @action(detail=False, methods=['get'])
    def unlocked(self, request):
        """
        Get videos that are unlocked for the current user
        First video is always unlocked
        A video is unlocked if the previous video has been passed
        """
        user = request.user
        videos = Video.objects.all().order_by('sequence_number')
        unlocked_videos = []
        
        # First video is always unlocked
        if videos.exists():
            first_video = videos.first()
            unlocked_videos.append(first_video)
            
            # Check if subsequent videos are unlocked
            for i in range(1, len(videos)):
                previous_video = videos[i-1]
                # Check if user has passed the previous video
                attempts = QuizAttempt.objects.filter(
                    user=user, 
                    video=previous_video, 
                    is_passed=True
                )
                
                if attempts.exists():
                    unlocked_videos.append(videos[i])
                else:
                    break
        
        serializer = VideoListSerializer(unlocked_videos, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['get'])
    def can_attempt(self, request, pk=None):
        """
        Check if a user can attempt a video quiz
        - Video must be unlocked
        - User must have fewer than 2 attempts or passed already
        """
        user = request.user
        video = self.get_object()
        
        # Check if video is unlocked
        videos = Video.objects.filter(sequence_number__lt=video.sequence_number).order_by('sequence_number')
        
        if videos.exists():
            # Check if all previous videos have been passed
            for prev_video in videos:
                attempts = QuizAttempt.objects.filter(user=user, video=prev_video, is_passed=True)
                if not attempts.exists():
                    return Response({
                        "can_attempt": False,
                        "reason": "Previous videos must be passed first."
                    })
        
        # Check number of attempts
        attempts = QuizAttempt.objects.filter(user=user, video=video)
        attempts_count = attempts.count()
        
        # Check if user has already passed
        if attempts.filter(is_passed=True).exists():
            passed_attempt = attempts.filter(is_passed=True).first()
            return Response({
                "can_attempt": False,
                "reason": "You have already passed this quiz. Move on to the next video.",
                "attempts_left": 0,
                "status": "passed",
                "attempts_used": attempts_count,
                "is_passed": True,
                "percentage": passed_attempt.percentage if passed_attempt else None
            })
        if attempts_count >= 2:
            return Response({
                "can_attempt": False,
                "reason": "Maximum attempts reached",
                "attempts_left": 0,
                "status": "max_attempts",
                "attempts_used": attempts_count
            })
        
        # Check if there's an in-progress attempt
        in_progress = attempts.filter(status='in_progress').first()
        if in_progress:
            return Response({
                "can_attempt": True,
                "reason": "Quiz in progress",
                "attempts_left": 2 - attempts_count,
                "status": "resume",
                "attempt_id": in_progress.id,
                "time_remaining": in_progress.time_remaining,
                "attempts_used": attempts_count
            })
        
        return Response({
            "can_attempt": True,
            "reason": "Can attempt quiz",
            "attempts_left": 2 - attempts_count,
            "status": "start",
            "attempts_used": attempts_count
        })
        
    @action(detail=True, methods=['get'])
    def stream_video(self, request, pk=None):
        """
        Stream video file with proper headers for seeking
        """
        video = self.get_object()
        if not video.video_file:
            return Response({"error": "No video file available"}, status=status.HTTP_404_NOT_FOUND)
            
        video_path = os.path.join(settings.MEDIA_ROOT, str(video.video_file))
        
        if not os.path.exists(video_path):
            return Response({"error": "Video file not found"}, status=status.HTTP_404_NOT_FOUND)
            
        # Get file size
        file_size = os.path.getsize(video_path)
        
        # Get content type
        content_type = mimetypes.guess_type(video_path)[0] or 'video/mp4'
        
        # Handle range requests
        range_header = request.META.get('HTTP_RANGE', '').strip()
        range_match = range_header.replace('bytes=', '').split('-')
        start = int(range_match[0]) if range_match[0] else 0
        end = int(range_match[1]) if range_match[1] else file_size - 1
        
        # Ensure the range is valid
        end = min(end, file_size - 1)
        length = end - start + 1
        
        # Create response
        response = FileResponse(
            open(video_path, 'rb'),
            content_type=content_type,
            status=206 if range_header else 200
        )
        
        # Set headers for range request
        if range_header:
            response['Content-Range'] = f'bytes {start}-{end}/{file_size}'
        
        response['Accept-Ranges'] = 'bytes'
        response['Content-Length'] = str(length)
        
        return response