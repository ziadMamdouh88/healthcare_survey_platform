from django.db import models
from django.contrib.auth.models import User
from survey_management.models.department import Department

class Survey(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField()
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='created_surveys')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)
    departments = models.ManyToManyField(Department, related_name='surveys', blank=True)
    
    # For targeting specific user segments
    target_audience = models.CharField(max_length=255, blank=True, null=True, 
                                      help_text="Description of the target audience")
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Survey'
        verbose_name_plural = 'Surveys'
    
    def __str__(self):
        return self.title
    
    def get_completion_rate(self):
        """Calculate the completion rate of this survey"""
        total_responses = self.responses.count()
        if total_responses == 0:
            return 0
        completed_responses = self.responses.filter(is_complete=True).count()
        return (completed_responses / total_responses) * 100
    
    def get_average_rating(self):
        """Calculate the average rating for rating questions in this survey"""
        from survey_management.models.response import ResponseItem
        rating_responses = ResponseItem.objects.filter(
            response__survey=self,
            question__question_type='RATING',
            numeric_answer__isnull=False
        )
        if not rating_responses.exists():
            return None
        return rating_responses.aggregate(models.Avg('numeric_answer'))['numeric_answer__avg']


class Question(models.Model):
    QUESTION_TYPES = (
        ('TEXT', 'Text'),
        ('MULTIPLE_CHOICE', 'Multiple Choice'),
        ('RATING', 'Rating'),
        ('BOOLEAN', 'Yes/No'),
    )
    
    survey = models.ForeignKey(Survey, on_delete=models.CASCADE, related_name='questions')
    text = models.TextField()
    question_type = models.CharField(max_length=20, choices=QUESTION_TYPES)
    is_required = models.BooleanField(default=False)
    order = models.PositiveIntegerField(default=0)
    
    # For rating questions
    min_rating = models.IntegerField(null=True, blank=True)
    max_rating = models.IntegerField(null=True, blank=True)
    
    class Meta:
        ordering = ['order']
    
    def __str__(self):
        return f"{self.text} ({self.get_question_type_display()})"


class QuestionOption(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name='options')
    text = models.CharField(max_length=255)
    order = models.PositiveIntegerField(default=0)
    
    class Meta:
        ordering = ['order']
    
    def __str__(self):
        return self.text
