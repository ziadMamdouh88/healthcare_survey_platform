from django.db.models import Avg, Count, Sum, F, Q
from django.utils import timezone
from datetime import timedelta
from survey_management.models.survey import Survey, Question
from survey_management.models.response import Response, ResponseItem

class AnalyticsService:
    """Service for generating analytics from survey responses"""
    
    def get_survey_completion_stats(self, survey_id=None, department_id=None, date_range=None):
        """
        Get completion statistics for surveys
        
        Args:
            survey_id: Optional ID to filter by specific survey
            department_id: Optional ID to filter by department
            date_range: Optional tuple of (start_date, end_date)
            
        Returns:
            Dictionary with completion statistics
        """
        # Start with all surveys
        surveys = Survey.objects.all()
        
        # Apply filters
        if survey_id:
            surveys = surveys.filter(id=survey_id)
        
        if department_id:
            surveys = surveys.filter(departments__id=department_id)
        
        # Prepare results
        results = []
        
        for survey in surveys:
            # Get responses for this survey
            responses = survey.responses.all()
            
            # Apply date filter if provided
            if date_range:
                start_date, end_date = date_range
                responses = responses.filter(
                    submitted_at__gte=start_date,
                    submitted_at__lte=end_date
                )
            
            # Calculate statistics
            total_responses = responses.count()
            completed_responses = responses.filter(is_complete=True).count()
            
            completion_rate = 0
            if total_responses > 0:
                completion_rate = (completed_responses / total_responses) * 100
            
            # Add to results
            results.append({
                'survey_id': survey.id,
                'survey_title': survey.title,
                'total_responses': total_responses,
                'completed_responses': completed_responses,
                'completion_rate': completion_rate
            })
        
        return results
    
    def get_rating_question_stats(self, question_id=None, survey_id=None, department_id=None):
        """
        Get statistics for rating questions
        
        Args:
            question_id: Optional ID to filter by specific question
            survey_id: Optional ID to filter by survey
            department_id: Optional ID to filter by department
            
        Returns:
            Dictionary with rating statistics
        """
        # Get rating questions
        questions = Question.objects.filter(question_type='RATING')
        
        # Apply filters
        if question_id:
            questions = questions.filter(id=question_id)
        
        if survey_id:
            questions = questions.filter(survey_id=survey_id)
        
        if department_id:
            questions = questions.filter(survey__departments__id=department_id)
        
        # Prepare results
        results = []
        
        for question in questions:
            # Get response items for this question
            items = ResponseItem.objects.filter(
                question=question,
                numeric_answer__isnull=False
            )
            
            # Calculate statistics
            count = items.count()
            
            if count > 0:
                avg_rating = items.aggregate(avg=Avg('numeric_answer'))['avg']
                min_rating = items.aggregate(min=Min('numeric_answer'))['min']
                max_rating = items.aggregate(max=Max('numeric_answer'))['max']
                
                # Add to results
                results.append({
                    'question_id': question.id,
                    'question_text': question.text,
                    'survey_id': question.survey.id,
                    'survey_title': question.survey.title,
                    'response_count': count,
                    'average_rating': avg_rating,
                    'min_rating': min_rating,
                    'max_rating': max_rating
                })
        
        return results
    
    def get_response_trend_data(self, days=30, survey_id=None, department_id=None):
        """
        Get trend data for responses over time
        
        Args:
            days: Number of days to include in the trend
            survey_id: Optional ID to filter by survey
            department_id: Optional ID to filter by department
            
        Returns:
            List of daily response counts
        """
        # Calculate date range
        end_date = timezone.now()
        start_date = end_date - timedelta(days=days)
        
        # Get responses in date range
        responses = Response.objects.filter(
            submitted_at__gte=start_date,
            submitted_at__lte=end_date
        )
        
        # Apply filters
        if survey_id:
            responses = responses.filter(survey_id=survey_id)
        
        if department_id:
            responses = responses.filter(survey__departments__id=department_id)
        
        # Group by day and count
        from django.db.models.functions import TruncDay
        daily_counts = responses.annotate(
            day=TruncDay('submitted_at')
        ).values('day').annotate(
            count=Count('id')
        ).order_by('day')
        
        # Format results
        results = [{
            'date': item['day'].strftime('%Y-%m-%d'),
            'response_count': item['count']
        } for item in daily_counts]
        
        return results
