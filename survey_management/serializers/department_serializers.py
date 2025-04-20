from rest_framework import serializers
from survey_management.models.department import Department

class DepartmentSerializer(serializers.ModelSerializer):
    staff_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Department
        fields = ['id', 'name', 'description', 'staff_count']
    
    def get_staff_count(self, obj):
        return obj.staff.count()
