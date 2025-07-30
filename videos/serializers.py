from rest_framework import serializers
from .models import Video

class VideoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Video
        fields = '__all__'

class VideoListSerializer(serializers.ModelSerializer):
    """Serializer for listing videos with basic information"""
    
    class Meta:
        model = Video
        fields = ['id', 'title', 'description', 'sequence_number', 'passing_percentage', 'time_limit', 'is_active']