from rest_framework import serializers
from survey_management.models.survey import Survey, Question, QuestionOption

class QuestionOptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = QuestionOption
        fields = ['id', 'text', 'order']

class QuestionSerializer(serializers.ModelSerializer):
    options = QuestionOptionSerializer(many=True, read_only=False, required=False)
    
    class Meta:
        model = Question
        fields = ['id', 'text', 'question_type', 'is_required', 'order', 
                 'min_rating', 'max_rating', 'options']
    
    def create(self, validated_data):
        options_data = validated_data.pop('options', [])
        question = Question.objects.create(**validated_data)
        
        for option_data in options_data:
            QuestionOption.objects.create(question=question, **option_data)
        
        return question
    
    def update(self, instance, validated_data):
        options_data = validated_data.pop('options', None)
        
        # Update question fields
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        
        # Update options if provided
        if options_data is not None:
            instance.options.all().delete()
            for option_data in options_data:
                QuestionOption.objects.create(question=instance, **option_data)
        
        return instance

class SurveySerializer(serializers.ModelSerializer):
    questions = QuestionSerializer(many=True, read_only=True, required=False)
    created_by = serializers.ReadOnlyField(source='created_by.username')
    completion_rate = serializers.SerializerMethodField()
    average_rating = serializers.SerializerMethodField()
    
    class Meta:
        model = Survey
        fields = ['id', 'title', 'description', 'created_by', 'created_at', 
                 'updated_at', 'is_active', 'departments', 'target_audience',
                 'questions', 'completion_rate', 'average_rating']
    
    def get_completion_rate(self, obj):
        return obj.get_completion_rate()
    
    def get_average_rating(self, obj):
        return obj.get_average_rating()
