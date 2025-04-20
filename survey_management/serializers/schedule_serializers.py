from rest_framework import serializers
from survey_management.models.schedule import SurveySchedule

class SurveyScheduleSerializer(serializers.ModelSerializer):
    survey_title = serializers.ReadOnlyField(source='survey.title')
    
    class Meta:
        model = SurveySchedule
        fields = ['id', 'survey', 'survey_title', 'trigger_event', 'delay_hours', 
                 'is_active', 'event_filter', 'send_email', 'send_sms', 
                 'created_at', 'updated_at']
