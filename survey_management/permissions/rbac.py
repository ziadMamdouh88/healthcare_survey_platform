from rest_framework import permissions

class IsAdminOrReadOnly(permissions.BasePermission):
    """
    Custom permission to only allow admins to edit objects.
    """
    def has_permission(self, request, view):
        # Superusers always have permission
        if request.user.is_superuser:
            return True
            
        # Read permissions are allowed to any authenticated user
        if request.method in permissions.SAFE_METHODS:
            return request.user.is_authenticated
        
        # Write permissions are only allowed to admins
        return (request.user.is_authenticated and 
                hasattr(request.user, 'profile') and 
                request.user.profile.role == 'ADMIN')

class HasSurveyPermission(permissions.BasePermission):
    """
    Custom permission for survey-related operations.
    """
    def has_permission(self, request, view):
        # Superusers always have permission
        if request.user.is_superuser:
            return True
            
        if not request.user.is_authenticated:
            return False
        
        # Check if user has the required permission based on the action
        if view.action in ['create', 'update', 'partial_update', 'destroy']:
            return (hasattr(request.user, 'profile') and 
                    request.user.profile.has_permission('create_survey'))
        
        elif view.action == 'export_responses':
            return (hasattr(request.user, 'profile') and 
                    request.user.profile.has_permission('export_data'))
        
        elif view.action == 'assign_survey':
            return (hasattr(request.user, 'profile') and 
                    request.user.profile.has_permission('assign_survey'))
        
        # Read permissions are allowed to any authenticated user
        return True
    
    def has_object_permission(self, request, view, obj):
        # Superusers always have permission
        if request.user.is_superuser:
            return True
            
        # Read permissions are allowed to any authenticated user
        if request.method in permissions.SAFE_METHODS:
            # Staff can only view surveys for their department
            if (hasattr(request.user, 'profile') and 
                request.user.profile.role == 'STAFF' and 
                request.user.profile.department):
                return request.user.profile.department in obj.departments.all()
            return True
        
        # Write permissions are only allowed to admins or the creator
        return ((hasattr(request.user, 'profile') and 
                request.user.profile.role == 'ADMIN') or 
                obj.created_by == request.user)

class HasResponsePermission(permissions.BasePermission):
    """
    Custom permission for response-related operations.
    """
    def has_permission(self, request, view):
        # Superusers always have permission
        if request.user.is_superuser:
            return True
            
        if not request.user.is_authenticated:
            return False
        
        # Patients can only submit responses
        if hasattr(request.user, 'profile') and request.user.profile.role == 'PATIENT':
            return view.action in ['submit', 'create', 'retrieve', 'list']
        
        # Staff can view responses but not modify them
        elif hasattr(request.user, 'profile') and request.user.profile.role == 'STAFF':
            return request.method in permissions.SAFE_METHODS
        
        # Admins have full access
        elif hasattr(request.user, 'profile') and request.user.profile.role == 'ADMIN':
            return True
        
        return False
    
    def has_object_permission(self, request, view, obj):
        # Superusers always have permission
        if request.user.is_superuser:
            return True
            
        # Patients can only access their own responses
        if hasattr(request.user, 'profile') and request.user.profile.role == 'PATIENT':
            return obj.respondent == request.user
        
        # Staff can only view responses for their department
        elif (hasattr(request.user, 'profile') and 
              request.user.profile.role == 'STAFF' and 
              request.user.profile.department):
            return request.user.profile.department in obj.survey.departments.all()
        
        # Admins have full access
        elif hasattr(request.user, 'profile') and request.user.profile.role == 'ADMIN':
            return True
        
        return False

class HasAnalyticsPermission(permissions.BasePermission):
    """
    Custom permission for analytics-related operations.
    """
    def has_permission(self, request, view):
        # Superusers always have permission
        if request.user.is_superuser:
            return True
            
        if not request.user.is_authenticated:
            return False
        
        # Only staff and admins can access analytics
        return (hasattr(request.user, 'profile') and 
                request.user.profile.has_permission('view_analytics'))
