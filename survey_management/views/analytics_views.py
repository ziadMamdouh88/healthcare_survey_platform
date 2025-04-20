from rest_framework import viewsets, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db.models import Avg, Count, F, Q
from django.utils import timezone
from datetime import timedelta
from survey_management.models.survey import Survey
from survey_management.models.response import ResponseItem
from survey_management.permissions.rbac import HasAnalyticsPermission

class AnalyticsViewSet(viewsets.ViewSet):
    """
    ViewSet for survey analytics
    """
    permission_classes = [permissions.IsAuthenticated, HasAnalyticsPermission]
    
    @action(detail=False, methods=['get'])
    def completion_rates(self, request):
        """Get completion rates for all surveys"""
        surveys = Survey.objects.all()
        
        # Filter by department if staff user
        if request.user.profile.role == 'STAFF' and request.user.profile.department:
            surveys = surveys.filter(departments=request.user.profile.department)
        
        data = []
        for survey in surveys:
            total_responses = survey.responses.count()
            completed_responses = survey.responses.filter(is_complete=True).count()
            
            completion_rate = 0
            if total_responses > 0:
                completion_rate = (completed_responses / total_responses) * 100
            
            data.append({
                'survey_id': survey.id,
                'survey_title': survey.title,
                'total_responses': total_responses,
                'completed_responses': completed_responses,
                'completion_rate': completion_rate
            })
        
        return Response(data)
    
    @action(detail=False, methods=['get'])
    def rating_averages(self, request):
        """Get average ratings for all surveys with rating questions"""
        # Get all rating questions
        from survey_management.models.survey import Question
        rating_questions = Question.objects.filter(question_type='RATING')
        
        # Filter by department if staff user
        if request.user.profile.role == 'STAFF' and request.user.profile.department:
            rating_questions = rating_questions.filter(
                survey__departments=request.user.profile.department
            )
        
        data = []
        for question in rating_questions:
            # Calculate average rating
            avg_rating = ResponseItem.objects.filter(
                question=question,
                numeric_answer__isnull=False
            ).aggregate(avg=Avg('numeric_answer'))['avg']
            
            if avg_rating is not None:
                data.append({
                    'survey_id': question.survey.id,
                    'survey_title': question.survey.title,
                    'question_id': question.id,
                    'question_text': question.text,
                    'average_rating': avg_rating,
                    'min_rating': question.min_rating,
                    'max_rating': question.max_rating
                })
        
        return Response(data)
    
    @action(detail=False, methods=['get'])
    def response_trends(self, request):
        """Get response trends over time"""
        # Get date range from query params (default to last 30 days)
        days = int(request.query_params.get('days', 30))
        end_date = timezone.now()
        start_date = end_date - timedelta(days=days)
        
        # Get all responses in the date range
        from survey_management.models.response import Response as SurveyResponse
        responses = SurveyResponse.objects.filter(
            submitted_at__gte=start_date,
            submitted_at__lte=end_date
        )
        
        # Filter by department if staff user
        if request.user.profile.role == 'STAFF' and request.user.profile.department:
            responses = responses.filter(
                survey__departments=request.user.profile.department
            )
        
        # Group by day and count
        from django.db.models.functions import TruncDay
        daily_counts = responses.annotate(
            day=TruncDay('submitted_at')
        ).values('day').annotate(
            count=Count('id')
        ).order_by('day')
        
        data = [{
            'date': item['day'].strftime('%Y-%m-%d'),
            'response_count': item['count']
        } for item in daily_counts]
        
        return Response(data)
    
    @action(detail=True, methods=['get'])
    def multiple_choice_distribution(self, request, pk=None):
        """Get distribution of answers for multiple choice questions in a survey"""
        try:
            survey = Survey.objects.get(pk=pk)
        except Survey.DoesNotExist:
            return Response({'detail': 'Survey not found'}, status=404)
        
        # Check department access for staff
        if (request.user.profile.role == 'STAFF' and 
            request.user.profile.department and 
            request.user.profile.department not in survey.departments.all()):
            return Response({'detail': 'Access denied'}, status=403)
        
        # Get all multiple choice questions for this survey
        multiple_choice_questions = survey.questions.filter(question_type='MULTIPLE_CHOICE')
        
        data = []
        for question in multiple_choice_questions:
            # Get distribution of selected options
            options = question.options.all()
            option_counts = []
            
            for option in options:
                count = ResponseItem.objects.filter(
                    question=question,
                    selected_option=option
                ).count()
                
                option_counts.append({
                    'option_id': option.id,
                    'option_text': option.text,
                    'count': count
                })
            
            data.append({
                'question_id': question.id,
                'question_text': question.text,
                'options': option_counts
            })
        
        return Response(data)
