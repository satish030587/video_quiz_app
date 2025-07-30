from rest_framework import serializers
from .models import User, UserProgress, Certificate

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name', 'profile_picture', 'is_superadmin']
        read_only_fields = ['id', 'is_superadmin']

class UserCreateSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'password', 'profile_picture']

    def create(self, validated_data):
        password = validated_data.pop('password')
        user = User(**validated_data)
        user.set_password(password)
        user.save()
        
        # Create user progress record
        UserProgress.objects.create(user=user)
        
        return user

class UserProgressSerializer(serializers.ModelSerializer):
    videos_passed = serializers.SerializerMethodField()
    videos_failed = serializers.SerializerMethodField()
    
    class Meta:
        model = UserProgress
        fields = '__all__'
        
    def get_videos_passed(self, obj):
        """Return list of passed video objects with id and title"""
        return [{'id': video.id, 'title': video.title} for video in obj.videos_passed.all()]
        
    def get_videos_failed(self, obj):
        """Return list of failed video objects with id and title"""
        return [{'id': video.id, 'title': video.title} for video in obj.videos_failed.all()]

class CertificateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Certificate
        fields = '__all__'
        read_only_fields = ['unique_id', 'issue_date', 'user']