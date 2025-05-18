from rest_framework import serializers
from .models import Event, EventPhoto
from django.contrib.auth.models import User

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email']

class EventPhotoSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    
    class Meta:
        model = EventPhoto
        fields = ['id', 'image', 'caption', 'created_at', 'user']

class EventSerializer(serializers.ModelSerializer):
    creator = UserSerializer(read_only=True)
    participants = UserSerializer(many=True, read_only=True)
    photos = EventPhotoSerializer(many=True, read_only=True)
    is_participant = serializers.SerializerMethodField()
    can_join = serializers.SerializerMethodField()
    
    class Meta:
        model = Event
        fields = [
            'id', 'title', 'description', 'date', 'location',
            'max_participants', 'creator', 'participants',
            'created_at', 'updated_at', 'image', 'is_private',
            'photos', 'is_participant', 'can_join'
        ]
    
    def get_is_participant(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return request.user in obj.participants.all()
        return False
    
    def get_can_join(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return not obj.is_full and request.user not in obj.participants.all()
        return False 