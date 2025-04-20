from rest_framework import viewsets, permissions
from survey_management.models.department import Department
from survey_management.serializers.department_serializers import DepartmentSerializer
from survey_management.permissions.rbac import IsAdminOrReadOnly

class DepartmentViewSet(viewsets.ModelViewSet):
    queryset = Department.objects.all()
    serializer_class = DepartmentSerializer
    permission_classes = [permissions.IsAuthenticated, IsAdminOrReadOnly]
    search_fields = ['name', 'description']
