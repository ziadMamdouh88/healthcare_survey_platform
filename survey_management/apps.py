from django.apps import AppConfig


class SurveyManagementConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'survey_management'

    def ready(self):
        import survey_management.signals
