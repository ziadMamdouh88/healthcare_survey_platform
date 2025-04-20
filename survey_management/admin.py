from django.contrib import admin
from survey_management.models.survey import Survey, Question, QuestionOption
from survey_management.models.response import Response, ResponseItem
from survey_management.models.department import Department
from survey_management.models.schedule import SurveySchedule
from survey_management.models.audit import AuditLog

class QuestionOptionInline(admin.TabularInline):
    model = QuestionOption
    extra = 1

class QuestionInline(admin.TabularInline):
    model = Question
    extra = 1

@admin.register(Survey)
class SurveyAdmin(admin.ModelAdmin):
    list_display = ('title', 'description', 'created_by', 'created_at', 'is_active')
    list_filter = ('is_active', 'created_at')
    search_fields = ('title', 'description')
    inlines = [QuestionInline]

@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display = ('text', 'survey', 'question_type', 'is_required')
    list_filter = ('question_type', 'is_required')
    search_fields = ('text', 'survey__title')
    inlines = [QuestionOptionInline]

@admin.register(Response)
class ResponseAdmin(admin.ModelAdmin):
    list_display = ('survey', 'respondent', 'submitted_at', 'is_complete')
    list_filter = ('is_complete', 'submitted_at')
    search_fields = ('survey__title', 'respondent__username')

@admin.register(ResponseItem)
class ResponseItemAdmin(admin.ModelAdmin):
    list_display = ('response', 'question', 'get_answer')
    search_fields = ('response__survey__title', 'question__text')
    
    def get_answer(self, obj):
        if obj.text_answer:
            return obj.text_answer[:50]
        elif obj.numeric_answer is not None:
            return obj.numeric_answer
        elif obj.selected_option:
            return obj.selected_option.text
        return "No answer"
    get_answer.short_description = 'Answer'

@admin.register(Department)
class DepartmentAdmin(admin.ModelAdmin):
    list_display = ('name', 'description')
    search_fields = ('name', 'description')

@admin.register(SurveySchedule)
class SurveyScheduleAdmin(admin.ModelAdmin):
    list_display = ('survey', 'trigger_event', 'delay_hours', 'is_active')
    list_filter = ('trigger_event', 'is_active')
    search_fields = ('survey__title', 'trigger_event')

@admin.register(AuditLog)
class AuditLogAdmin(admin.ModelAdmin):
    list_display = ('user', 'action', 'timestamp', 'ip_address')
    list_filter = ('action', 'timestamp')
    search_fields = ('user__username', 'action', 'details')
    readonly_fields = ('user', 'action', 'details', 'timestamp', 'ip_address')
