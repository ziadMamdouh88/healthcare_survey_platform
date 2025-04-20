from rest_framework import serializers
from survey_management.models.response import Response, ResponseItem
from survey_management.models.survey import Question, QuestionOption

class ResponseItemSerializer(serializers.ModelSerializer):
    question_text = serializers.ReadOnlyField(source='question.text')
    question_type = serializers.ReadOnlyField(source='question.question_type')
    answer_display = serializers.ReadOnlyField(source='get_answer_display')
    
    class Meta:
        model = ResponseItem
        fields = ['id', 'question', 'question_text', 'question_type', 
                 'text_answer', 'numeric_answer', 'selected_option', 
                 'answer_display', 'created_at', 'updated_at']
    
    def validate(self, data):
        """Validate that the answer matches the question type"""
        question = data.get('question')
        text_answer = data.get('text_answer')
        numeric_answer = data.get('numeric_answer')
        selected_option = data.get('selected_option')
        
        if question.question_type == 'TEXT' and not text_answer:
            if question.is_required:
                raise serializers.ValidationError("Text answer is required for this question")
        
        elif question.question_type == 'MULTIPLE_CHOICE' and not selected_option:
            if question.is_required:
                raise serializers.ValidationError("An option must be selected for this question")
            
        elif question.question_type == 'RATING' and numeric_answer is None:
            if question.is_required:
                raise serializers.ValidationError("Rating is required for this question")
            
        elif question.question_type == 'BOOLEAN' and numeric_answer is None:
            if question.is_required:
                raise serializers.ValidationError("Yes/No answer is required for this question")
        
        return data

class ResponseSerializer(serializers.ModelSerializer):
    items = ResponseItemSerializer(many=True, read_only=True)
    respondent_username = serializers.ReadOnlyField(source='respondent.username')
    survey_title = serializers.ReadOnlyField(source='survey.title')
    completion_percentage = serializers.SerializerMethodField()
    
    class Meta:
        model = Response
        fields = ['id', 'survey', 'survey_title', 'respondent', 'respondent_username',
                 'started_at', 'submitted_at', 'is_complete', 'items', 'completion_percentage']
    
    def get_completion_percentage(self, obj):
        return obj.calculate_completion_percentage()

class SubmitResponseSerializer(serializers.Serializer):
    """Serializer for submitting a complete response with all answers"""
    survey_id = serializers.IntegerField()
    answers = serializers.ListField(
        child=serializers.DictField(
            child=serializers.CharField(allow_null=True, allow_blank=True)
        )
    )
    
    def validate_survey_id(self, value):
        from survey_management.models.survey import Survey
        try:
            survey = Survey.objects.get(pk=value, is_active=True)
            return value
        except Survey.DoesNotExist:
            raise serializers.ValidationError("Survey does not exist or is not active")
    
    def validate(self, data):
        from survey_management.models.survey import Survey, Question
        
        survey_id = data.get('survey_id')
        answers = data.get('answers', [])
        
        # Get all questions for this survey
        survey = Survey.objects.get(pk=survey_id)
        questions = Question.objects.filter(survey=survey)
        question_ids = set(q.id for q in questions)
        
        # Check that all required questions are answered
        for answer in answers:
            if 'question_id' not in answer:
                raise serializers.ValidationError("Each answer must include a question_id")
            
            try:
                question_id = int(answer['question_id'])
            except (ValueError, TypeError):
                raise serializers.ValidationError("question_id must be an integer")
            
            if question_id not in question_ids:
                raise serializers.ValidationError(f"Question {question_id} does not belong to this survey")
        
        # Check for missing required questions
        answered_question_ids = set(int(a['question_id']) for a in answers if 'question_id' in a)
        required_question_ids = set(q.id for q in questions if q.is_required)
        missing_required = required_question_ids - answered_question_ids
        
        if missing_required:
            raise serializers.ValidationError(f"Missing answers for required questions: {missing_required}")
        
        return data
