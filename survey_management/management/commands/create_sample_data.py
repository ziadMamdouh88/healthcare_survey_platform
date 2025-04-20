from django.core.management.base import BaseCommand
from survey_management.models.department import Department

class Command(BaseCommand):
    help = 'Creates sample departments for the application'

    def handle(self, *args, **options):
        # Create departments
        departments = [
            {'name': 'Cardiology', 'description': 'Heart-related healthcare'},
            {'name': 'Neurology', 'description': 'Brain and nervous system care'},
            {'name': 'Pediatrics', 'description': 'Healthcare for children'},
            {'name': 'Oncology', 'description': 'Cancer treatment and care'},
            {'name': 'Orthopedics', 'description': 'Bone and joint care'}
        ]
        
        created = 0
        for dept_data in departments:
            dept, was_created = Department.objects.get_or_create(
                name=dept_data['name'],
                defaults={'description': dept_data['description']}
            )
            if was_created:
                created += 1
                self.stdout.write(f"Created department: {dept.name}")
            else:
                self.stdout.write(f"Department already exists: {dept.name}")
        
        self.stdout.write(self.style.SUCCESS(f"Successfully created {created} departments"))
