from django.db import models
from survey_management.models.survey import Survey

class SurveySchedule(models.Model):
    TRIGGER_EVENTS = (
        ('APPOINTMENT_COMPLETED', 'Appointment Completed'),
        ('DISCHARGE', 'Patient Discharge'),
        ('MEDICATION_PRESCRIBED', 'Medication Prescribed'),
        ('PROCEDURE_COMPLETED', 'Procedure Completed'),
        ('MANUAL', 'Manual Trigger'),
    )
    
    survey = models.ForeignKey(Survey, on_delete=models.CASCADE, related_name='schedules')
    trigger_event = models.CharField(max_length=50, choices=TRIGGER_EVENTS)
    delay_hours = models.PositiveIntegerField(default=0, 
                                             help_text="Hours to wait after the trigger event before sending")
    is_active = models.BooleanField(default=True)
    
    # For event-specific filters
    event_filter = models.JSONField(blank=True, null=True, 
                                   help_text="JSON filter criteria for the trigger event")
    
    # Notification methods
    send_email = models.BooleanField(default=True)
    send_sms = models.BooleanField(default=False)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.survey.title} - {self.get_trigger_event_display()}"
