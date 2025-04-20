from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response as DRF_Response
from survey_management.models.schedule import SurveySchedule
from survey_management.serializers.schedule_serializers import SurveyScheduleSerializer
from survey_management.permissions.rbac import IsAdminOrReadOnly

class SurveyScheduleViewSet(viewsets.ModelViewSet):
    queryset = SurveySchedule.objects.all()
    serializer_class = SurveyScheduleSerializer
    permission_classes = [permissions.IsAuthenticated, IsAdminOrReadOnly]
    filterset_fields = ['survey', 'trigger_event', 'is_active']
    
    @action(detail=True, methods=['post'])
    def trigger_manually(self, request, pk=None):
        """Manually trigger a scheduled survey"""
        schedule = self.get_object()
        
        # Check if user has permission to trigger surveys
        if not request.user.profile.has_permission('assign_survey'):
            return DRF_Response(
                {"detail": "You do not have permission to trigger surveys."},
                status=status.HTTP_403_FORBIDDEN
            )
        
        # Get target users from request
        user_ids = request.data.get('user_ids', [])
        if not user_ids:
            return DRF_Response(
                {"detail": "No users specified for survey assignment."},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Process the trigger
        from survey_management.services.notification_service import NotificationService
        notification = NotificationService()
        
        results = notification.process_manual_trigger(schedule, user_ids)
        
        return DRF_Response({
            "detail": "Survey triggered manually",
            "results": results
        })
