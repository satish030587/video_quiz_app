from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from django.contrib.auth import logout
from .models import User, UserProgress
from .serializers import UserSerializer, UserCreateSerializer, UserProgressSerializer
from .permissions import IsSuperAdmin

class UserViewSet(viewsets.ModelViewSet):
    """
    API endpoint for managing users
    """
    queryset = User.objects.all()
    serializer_class = UserSerializer
    
    def get_permissions(self):
        """
        Only superadmins can create, update, or delete users
        Users can retrieve their own info
        """
        if self.action in ['create', 'update', 'partial_update', 'destroy', 'list']:
            permission_classes = [IsSuperAdmin]
        else:
            permission_classes = [permissions.IsAuthenticated]
        return [permission() for permission in permission_classes]
    
    def get_serializer_class(self):
        if self.action == 'create':
            return UserCreateSerializer
        return UserSerializer
    
    @action(detail=False, methods=['get', 'put', 'patch'])
    def me(self, request):
        """Get or update current user's info"""
        if request.method == 'GET':
            serializer = self.get_serializer(request.user)
            return Response(serializer.data)
        else:
            # PUT or PATCH - update user profile
            # Always treat as partial update to avoid requiring all fields
            serializer = self.get_serializer(request.user, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=False, methods=['post'])
    def logout(self, request):
        """Logout the current user"""
        logout(request)
        return Response({"detail": "Successfully logged out."}, status=status.HTTP_200_OK)

class UserProgressViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API endpoint for user progress
    """
    serializer_class = UserProgressSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        if self.request.user.is_superadmin:
            return UserProgress.objects.all()
        return UserProgress.objects.filter(user=self.request.user)
    
    @action(detail=False, methods=['get'])
    def my_progress(self, request):
        """Get current user's progress"""
        try:
            progress = UserProgress.objects.get(user=request.user)
            # Recalculate progress to ensure it's up to date
            progress.recalculate_progress()
            serializer = self.get_serializer(progress)
            return Response(serializer.data)
        except UserProgress.DoesNotExist:
            return Response(
                {"detail": "Progress not found for this user."}, 
                status=status.HTTP_404_NOT_FOUND
            )
    
    @action(detail=False, methods=['post'], permission_classes=[IsSuperAdmin])
    def recalculate_all_progress(self, request):
        """Recalculate progress for all users (Super Admin only)"""
        try:
            updated_count = UserProgress.recalculate_all_progress()
            return Response({
                "detail": f"Successfully recalculated progress for {updated_count} users.",
                "updated_count": updated_count
            })
        except Exception as e:
            return Response(
                {"detail": f"Error recalculating progress: {str(e)}"}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @action(detail=True, methods=['post'], permission_classes=[IsSuperAdmin])
    def recalculate_progress(self, request, pk=None):
        """Recalculate progress for a specific user (Super Admin only)"""
        try:
            progress = self.get_object()
            result = progress.recalculate_progress()
            return Response({
                "detail": f"Successfully recalculated progress for {progress.user.username}.",
                "progress": result
            })
        except Exception as e:
            return Response(
                {"detail": f"Error recalculating progress: {str(e)}"}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @action(detail=True, methods=['post'], permission_classes=[IsSuperAdmin])
    def reset_progress(self, request, pk=None):
        """Reset progress for a specific user (Super Admin only)"""
        try:
            progress = self.get_object()
            progress.reset_progress()
            return Response({
                "detail": f"Successfully reset progress for {progress.user.username}."
            })
        except Exception as e:
            return Response(
                {"detail": f"Error resetting progress: {str(e)}"}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )