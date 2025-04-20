from django.db import models
from django.contrib.auth.models import User
from survey_management.models.survey import Survey, Question, QuestionOption

class Response(models.Model):
    survey = models.ForeignKey(Survey, on_delete=models.CASCADE, related_name='responses')
    respondent = models.ForeignKey(User, on_delete=models.CASCADE, related_name='survey_responses')
    started_at = models.DateTimeField(auto_now_add=True)
    submitted_at = models.DateTimeField(null=True, blank=True)
    is_complete = models.BooleanField(default=False)
    
    class Meta:
        ordering = ['-submitted_at', '-started_at']
    
    def __str__(self):
        return f"Response to {self.survey.title} by {self.respondent.username}"
    
    def calculate_completion_percentage(self):
        """Calculate what percentage of required questions have been answered"""
        required_questions = self.survey.questions.filter(is_required=True).count()
        if required_questions == 0:
            return 100
        
        answered_required = ResponseItem.objects.filter(
            response=self,
            question__is_required=True
        ).exclude(
            text_answer='',
            numeric_answer=None,
            selected_option=None
        ).count()
        
        return (answered_required / required_questions) * 100


class ResponseItem(models.Model):
    response = models.ForeignKey(Response, on_delete=models.CASCADE, related_name='items')
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    
    # Different answer types based on question type
    text_answer = models.TextField(blank=True, null=True)
    numeric_answer = models.IntegerField(blank=True, null=True)
    selected_option = models.ForeignKey(QuestionOption, on_delete=models.CASCADE, 
                                        null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ('response', 'question')
    
    def __str__(self):
        return f"Answer to {self.question.text}"
    
    def get_answer_display(self):
        """Return the answer in a human-readable format"""
        if self.question.question_type == 'TEXT':
            return self.text_answer
        elif self.question.question_type == 'MULTIPLE_CHOICE':
            return self.selected_option.text if self.selected_option else None
        elif self.question.question_type == 'RATING':
            return str(self.numeric_answer)
        elif self.question.question_type == 'BOOLEAN':
            if self.numeric_answer == 1:
                return 'Yes'
            elif self.numeric_answer == 0:
                return 'No'
            return None
        return None
