import csv
import json
from django.http import HttpResponse
from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response as DRF_Response
from survey_management.models.survey import Survey, Question
from survey_management.models.response import Response
from survey_management.serializers.survey_serializers import (
    SurveySerializer, QuestionSerializer
)
from survey_management.permissions.rbac import IsAdminOrReadOnly, HasSurveyPermission

class SurveyViewSet(viewsets.ModelViewSet):
    queryset = Survey.objects.all()
    serializer_class = SurveySerializer
    permission_classes = [permissions.IsAuthenticated, HasSurveyPermission]
    filterset_fields = ['is_active', 'departments']
    search_fields = ['title', 'description']
    
    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)
    
    @action(detail=True, methods=['get'])
    def export_responses(self, request, pk=None):
        """Export all responses for a survey as CSV"""
        survey = self.get_object()
        
        # Check if user has permission to export
        if not request.user.profile.has_permission('export_data'):
            return DRF_Response(
                {"detail": "You do not have permission to export data."},
                status=status.HTTP_403_FORBIDDEN
            )
        
        # Get all responses for this survey
        responses = Response.objects.filter(survey=survey)
        
        # Create CSV response
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = f'attachment; filename="{survey.title}_responses.csv"'
        
        writer = csv.writer(response)
        
        # Write header row with question texts
        questions = survey.questions.all().order_by('order')
        header = ['Respondent', 'Submitted At', 'Complete']
        header.extend([q.text for q in questions])
        writer.writerow(header)
        
        # Write response data
        for resp in responses:
            row = [
                resp.respondent.username,
                resp.submitted_at.strftime('%Y-%m-%d %H:%M:%S') if resp.submitted_at else 'Not submitted',
                'Yes' if resp.is_complete else 'No'
            ]
            
            # Add answers for each question
            for question in questions:
                try:
                    answer_item = resp.items.get(question=question)
                    row.append(answer_item.get_answer_display() or '')
                except:
                    row.append('')
            
            writer.writerow(row)
        
        # Log the export action
        from survey_management.models.audit import AuditLog
        AuditLog.objects.create(
            user=request.user,
            action='EXPORT',
            details=f"Exported responses for survey: {survey.title}"
        )
        
        return response
    
    @action(detail=True, methods=['post'])
    def assign_survey(self, request, pk=None, user_id=None):
        """Assign a survey to a specific user"""
        survey = self.get_object()
        
        # Check if user has permission to assign surveys
        if not request.user.profile.has_permission('assign_survey'):
            return DRF_Response(
                {"detail": "You do not have permission to assign surveys."},
                status=status.HTTP_403_FORBIDDEN
            )
        
        from django.contrib.auth.models import User
        try:
            target_user = User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return DRF_Response(
                {"detail": "User not found."},
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Create a new response object (not submitted yet)
        response = Response.objects.create(
            survey=survey,
            respondent=target_user,
            is_complete=False
        )
        
        # Send notification (mocked)
        from survey_management.services.notification_service import NotificationService
        notification = NotificationService()
        notification.send_survey_assignment(survey, target_user)
        
        return DRF_Response({
            "detail": f"Survey assigned to {target_user.username}",
            "response_id": response.id
        })


class QuestionViewSet(viewsets.ModelViewSet):
    queryset = Question.objects.all()
    serializer_class = QuestionSerializer
    permission_classes = [permissions.IsAuthenticated, IsAdminOrReadOnly]
    filterset_fields = ['survey', 'question_type', 'is_required']
