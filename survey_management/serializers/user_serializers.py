from rest_framework import serializers
from django.contrib.auth.models import User
from survey_management.models.user import UserProfile

class UserProfileSerializer(serializers.ModelSerializer):
    username = serializers.ReadOnlyField(source='user.username')
    email = serializers.ReadOnlyField(source='user.email')
    full_name = serializers.SerializerMethodField()
    
    class Meta:
        model = UserProfile
        fields = ['id', 'username', 'email', 'full_name', 'role', 'department', 
                 'phone_number', 'medical_record_number', 'position']
    
    def get_full_name(self, obj):
        return f"{obj.user.first_name} {obj.user.last_name}".strip()
