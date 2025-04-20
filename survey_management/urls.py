from django.urls import path, include
from rest_framework.routers import DefaultRouter
from survey_management.views.survey_views import SurveyViewSet, QuestionViewSet
from survey_management.views.response_views import ResponseViewSet, ResponseItemViewSet
from survey_management.views.analytics_views import AnalyticsViewSet
from survey_management.views.department_views import DepartmentViewSet
from survey_management.views.schedule_views import SurveyScheduleViewSet

# Create a router and register our viewsets
router = DefaultRouter()
router.register(r'surveys', SurveyViewSet)
router.register(r'questions', QuestionViewSet)
router.register(r'responses', ResponseViewSet)
router.register(r'response-items', ResponseItemViewSet)
router.register(r'departments', DepartmentViewSet)
router.register(r'schedules', SurveyScheduleViewSet)
router.register(r'analytics', AnalyticsViewSet, basename='analytics')

# The API URLs are determined automatically by the router
urlpatterns = [
    path('', include(router.urls)),
    path('auth/', include('rest_framework.urls')),
    # Custom endpoints
    path('surveys/<int:survey_id>/export/', 
         SurveyViewSet.as_view({'get': 'export_responses'}), 
         name='survey-export'),
    path('surveys/<int:survey_id>/assign/<int:user_id>/', 
         SurveyViewSet.as_view({'post': 'assign_survey'}), 
         name='assign-survey'),
]
