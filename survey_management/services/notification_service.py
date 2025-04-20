import logging
from django.core.mail import send_mail
from django.conf import settings
from django.contrib.auth.models import User
from survey_management.models.response import Response
from survey_management.models.schedule import SurveySchedule

logger = logging.getLogger(__name__)

class NotificationService:
    """Service for sending notifications about surveys"""
    
    def send_survey_assignment(self, survey, user):
        """
        Send notification to user about survey assignment
        
        Args:
            survey: Survey object
            user: User object
        
        Returns:
            Boolean indicating success
        """
        # Get user's email and phone
        email = user.email
        phone = user.profile.phone_number if hasattr(user, 'profile') else None
        
        # Log the notification
        logger.info(f"Sending survey assignment notification to {user.username} for survey: {survey.title}")
        
        # Send email notification (if email available)
        if email:
            try:
                subject = f"New Survey: {survey.title}"
                message = f"""
                Hello {user.first_name or user.username},
                
                You have been assigned a new survey: {survey.title}
                
                Please complete this survey at your earliest convenience.
                
                Thank you,
                Healthcare Survey Platform
                """
                
                # In production, this would actually send an email
                # For development, we're just logging it
                logger.info(f"Would send email to {email}: {subject}")
                
                # Uncomment to actually send email
                # send_mail(
                #     subject,
                #     message,
                #     settings.DEFAULT_FROM_EMAIL,
                #     [email],
                #     fail_silently=False,
                # )
                
            except Exception as e:
                logger.error(f"Failed to send email notification: {str(e)}")
                return False
        
        # Send SMS notification (if phone available)
        if phone:
            try:
                message = f"New survey assigned: {survey.title}. Please complete at your earliest convenience."
                
                # In production, this would integrate with an SMS service
                # For development, we're just logging it
                logger.info(f"Would send SMS to {phone}: {message}")
                
                # Example SMS integration (commented out)
                # twilio_client = Client(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)
                # twilio_client.messages.create(
                #     body=message,
                #     from_=settings.TWILIO_PHONE_NUMBER,
                #     to=phone
                # )
                
            except Exception as e:
                logger.error(f"Failed to send SMS notification: {str(e)}")
                # Continue even if SMS fails
        
        return True
    
    def process_manual_trigger(self, schedule, user_ids):
        """
        Process a manual trigger for a scheduled survey
        
        Args:
            schedule: SurveySchedule object
            user_ids: List of user IDs to assign the survey to
            
        Returns:
            Dictionary with results
        """
        survey = schedule.survey
        results = {
            'success': [],
            'failed': []
        }
        
        for user_id in user_ids:
            try:
                user = User.objects.get(pk=user_id)
                
                # Create a new response object
                response = Response.objects.create(
                    survey=survey,
                    respondent=user,
                    is_complete=False
                )
                
                # Send notification
                success = self.send_survey_assignment(survey, user)
                
                if success:
                    results['success'].append({
                        'user_id': user.id,
                        'username': user.username,
                        'response_id': response.id
                    })
                else:
                    results['failed'].append({
                        'user_id': user.id,
                        'username': user.username,
                        'reason': 'Notification failed'
                    })
                    
            except User.DoesNotExist:
                results['failed'].append({
                    'user_id': user_id,
                    'reason': 'User not found'
                })
            except Exception as e:
                results['failed'].append({
                    'user_id': user_id,
                    'reason': str(e)
                })
        
        return results
    
    def process_scheduled_surveys(self):
        """
        Process all scheduled surveys that are due
        
        Returns:
            Dictionary with results
        """
        # Get all active schedules
        schedules = SurveySchedule.objects.filter(is_active=True)
        
        results = {
            'processed': 0,
            'success': 0,
            'failed': 0
        }
        
        for schedule in schedules:
            # In a real implementation, this would check external systems
            # to find events that match the trigger criteria
            
            # For demonstration, we'll just log that we would process this schedule
            logger.info(f"Would process schedule: {schedule.id} - {schedule.survey.title} - {schedule.trigger_event}")
            
            # Increment processed count
            results['processed'] += 1
        
        return results
