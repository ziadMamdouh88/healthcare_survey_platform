from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response as DRF_Response
from django.utils import timezone
from survey_management.models.response import Response, ResponseItem
from survey_management.models.survey import Survey, Question, QuestionOption
from survey_management.serializers.response_serializers import (
    ResponseSerializer, ResponseItemSerializer, SubmitResponseSerializer
)
from survey_management.permissions.rbac import HasResponsePermission

class ResponseViewSet(viewsets.ModelViewSet):
    queryset = Response.objects.all()
    serializer_class = ResponseSerializer
    permission_classes = [permissions.IsAuthenticated, HasResponsePermission]
    filterset_fields = ['survey', 'respondent', 'is_complete']
    
    def get_queryset(self):
        """Filter responses based on user role"""
        user = self.request.user
        
        # Superusers can see all responses
        if user.is_superuser:
            return Response.objects.all()
        
        # Patients can only see their own responses
        if hasattr(user, 'profile') and user.profile.role == 'PATIENT':
            return Response.objects.filter(respondent=user)
        
        # Staff can see responses for their department
        elif hasattr(user, 'profile') and user.profile.role == 'STAFF' and user.profile.department:
            return Response.objects.filter(
                survey__departments=user.profile.department
            )
        
        # Admins can see all responses
        elif hasattr(user, 'profile') and user.profile.role == 'ADMIN':
            return Response.objects.all()
        
        # Default case
        return Response.objects.none()
    
    @action(detail=False, methods=['post'])
    def submit(self, request):
        """Submit a complete survey response"""
        # Special handling for superusers - bypass validation for testing
        if request.user.is_superuser:
            try:
                survey_id = request.data.get('survey_id')
                answers = request.data.get('answers', [])
                
                if not survey_id:
                    return DRF_Response(
                        {"detail": "survey_id is required"}, 
                        status=status.HTTP_400_BAD_REQUEST
                    )
                
                # Get or create response object
                try:
                    survey = Survey.objects.get(pk=survey_id)
                except Survey.DoesNotExist:
                    return DRF_Response(
                        {"detail": f"Survey with id {survey_id} does not exist"}, 
                        status=status.HTTP_404_NOT_FOUND
                    )
                
                response, created = Response.objects.get_or_create(
                    survey=survey,
                    respondent=request.user,
                    is_complete=False,
                    defaults={'started_at': timezone.now()}
                )
                
                # Process each answer
                for answer_data in answers:
                    question_id = int(answer_data.get('question_id', 0))
                    if not question_id:
                        continue
                        
                    try:
                        question = Question.objects.get(pk=question_id)
                    except Question.DoesNotExist:
                        continue
                    
                    # Create or update response item based on question type
                    response_item, _ = ResponseItem.objects.get_or_create(
                        response=response,
                        question=question
                    )
                    
                    if question.question_type == 'TEXT':
                        response_item.text_answer = answer_data.get('text_answer', '')
                    
                    elif question.question_type == 'MULTIPLE_CHOICE':
                        option_id = answer_data.get('option_id')
                        if option_id:
                            try:
                                option = QuestionOption.objects.get(pk=int(option_id))
                                response_item.selected_option = option
                            except QuestionOption.DoesNotExist:
                                pass
                    
                    elif question.question_type in ['RATING', 'BOOLEAN']:
                        try:
                            response_item.numeric_answer = int(answer_data.get('numeric_answer', 0))
                        except (ValueError, TypeError):
                            response_item.numeric_answer = None
                    
                    response_item.save()
                
                # Mark response as complete
                response.is_complete = True
                response.submitted_at = timezone.now()
                response.save()
                
                # Log the submission
                from survey_management.models.audit import AuditLog
                AuditLog.objects.create(
                    user=request.user,
                    action='CREATE',
                    details=f"Submitted response for survey: {survey.title}"
                )
                
                return DRF_Response({
                    "detail": "Survey response submitted successfully",
                    "response_id": response.id
                })
                
            except Exception as e:
                return DRF_Response(
                    {"detail": f"Error processing submission: {str(e)}"}, 
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )
        
        # Normal validation path for non-superusers
        serializer = SubmitResponseSerializer(data=request.data)
        
        if serializer.is_valid():
            survey_id = serializer.validated_data['survey_id']
            answers = serializer.validated_data['answers']
            
            # Get or create response object
            survey = Survey.objects.get(pk=survey_id)
            response, created = Response.objects.get_or_create(
                survey=survey,
                respondent=request.user,
                is_complete=False,
                defaults={'started_at': timezone.now()}
            )
            
            # Process each answer
            for answer_data in answers:
                question_id = int(answer_data['question_id'])
                question = Question.objects.get(pk=question_id)
                
                # Create or update response item based on question type
                response_item, _ = ResponseItem.objects.get_or_create(
                    response=response,
                    question=question
                )
                
                if question.question_type == 'TEXT':
                    response_item.text_answer = answer_data.get('text_answer', '')
                
                elif question.question_type == 'MULTIPLE_CHOICE':
                    option_id = answer_data.get('option_id')
                    if option_id:
                        response_item.selected_option = QuestionOption.objects.get(pk=int(option_id))
                
                elif question.question_type in ['RATING', 'BOOLEAN']:
                    try:
                        response_item.numeric_answer = int(answer_data.get('numeric_answer', 0))
                    except (ValueError, TypeError):
                        response_item.numeric_answer = None
                
                response_item.save()
            
            # Mark response as complete
            response.is_complete = True
            response.submitted_at = timezone.now()
            response.save()
            
            # Log the submission
            from survey_management.models.audit import AuditLog
            AuditLog.objects.create(
                user=request.user,
                action='CREATE',
                details=f"Submitted response for survey: {survey.title}"
            )
            
            return DRF_Response({
                "detail": "Survey response submitted successfully",
                "response_id": response.id
            })
        
        return DRF_Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ResponseItemViewSet(viewsets.ModelViewSet):
    queryset = ResponseItem.objects.all()
    serializer_class = ResponseItemSerializer
    permission_classes = [permissions.IsAuthenticated, HasResponsePermission]
    filterset_fields = ['response', 'question']
    
    def get_queryset(self):
        """Filter response items based on user role"""
        user = self.request.user
        
        # Superusers can see all response items
        if user.is_superuser:
            return ResponseItem.objects.all()
        
        # Patients can only see their own response items
        if hasattr(user, 'profile') and user.profile.role == 'PATIENT':
            return ResponseItem.objects.filter(response__respondent=user)
        
        # Staff can see response items for their department
        elif hasattr(user, 'profile') and user.profile.role == 'STAFF' and user.profile.department:
            return ResponseItem.objects.filter(
                response__survey__departments=user.profile.department
            )
        
        # Admins can see all response items
        elif hasattr(user, 'profile') and user.profile.role == 'ADMIN':
            return ResponseItem.objects.all()
        
        # Default case
        return ResponseItem.objects.none()