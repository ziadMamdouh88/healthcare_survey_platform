from django.db import models
from django.contrib.auth.models import User

class UserProfile(models.Model):
    USER_ROLES = (
        ('ADMIN', 'Healthcare Admin'),
        ('STAFF', 'Medical Staff'),
        ('PATIENT', 'Patient'),
        ('INTEGRATOR', 'System Integrator'),
    )
    
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    role = models.CharField(max_length=20, choices=USER_ROLES)
    department = models.ForeignKey('survey_management.Department', on_delete=models.SET_NULL, 
                                  null=True, blank=True, related_name='staff')
    phone_number = models.CharField(max_length=20, blank=True, null=True)
    
    # For patients
    medical_record_number = models.CharField(max_length=50, blank=True, null=True)
    
    # For staff/admin
    position = models.CharField(max_length=100, blank=True, null=True)
    
    # For system integrators
    api_key = models.CharField(max_length=64, blank=True, null=True)
    
    def __str__(self):
        return f"{self.user.username} ({self.get_role_display()})"
    
    def has_permission(self, permission_name):
        """Check if user has a specific permission based on role"""
        # Superusers have all permissions
        if self.user.is_superuser:
            return True
            
        role_permissions = {
            'ADMIN': ['create_survey', 'edit_survey', 'delete_survey', 'view_responses', 
                     'export_data', 'manage_users', 'view_analytics'],
            'STAFF': ['assign_survey', 'view_responses', 'view_analytics'],
            'PATIENT': ['submit_response'],
            'INTEGRATOR': ['api_access', 'trigger_survey'],
        }
        
        return permission_name in role_permissions.get(self.role, [])
