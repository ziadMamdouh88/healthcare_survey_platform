# Healthcare Survey Platform

A scalable backend system for managing healthcare surveys, supporting real-time survey distribution, secure data collection, analytics, and administrative tools.

## Overview

This Django-based application provides a comprehensive survey management system for healthcare providers. It allows clinics, hospitals, and health tech providers to create, manage, and analyze patient surveys such as post-visit satisfaction, symptom checkers, and service feedback.

## Features

### Survey Management API
- Create, edit, delete surveys with multiple question types (text, rating, multiple choice)
- Associate surveys with departments, events, or user segments
- Role-based access control for survey management

### Response Handling & Analytics
- Submit and store survey responses securely
- Aggregate basic analytics (average rating, completion rate)
- Export responses to CSV for reporting

### Scheduling & Delivery
- Schedule surveys for automatic delivery based on triggers
- Support email/SMS notification triggers (mocked)

### Security & Access
- Role-based access control (RBAC)
- Audit logging of survey creation and responses

### API Documentation
- Well-documented endpoints using Swagger/OpenAPI

## Architecture Decisions

### Data Modeling
- **Survey Model**: Core entity with questions and options
- **Response Model**: Captures user responses with flexible answer types
- **User Profiles**: Extended Django User with role-based permissions
- **Departments**: Organizational units for targeting surveys
- **Scheduling**: Flexible trigger system for automated survey delivery

### Security
- Role-based permissions for all operations
- Comprehensive audit logging
- Secure handling of patient data

### Scalability
- Modular design with separation of concerns
- Service-based architecture for business logic
- Efficient database queries with proper indexing

## Setup Instructions

1. Clone the repository
2. Create a virtual environment:
   \`\`\`
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   \`\`\`
3. Install dependencies:
   \`\`\`
   pip install -r requirements.txt
   \`\`\`
4. Run migrations:
   \`\`\`
   python manage.py migrate
   \`\`\`
5. Create a superuser:
   \`\`\`
   python manage.py createsuperuser
   \`\`\`
6. Run the development server:
   \`\`\`
   python manage.py runserver
   \`\`\`
7. Access the API at http://localhost:8000/api/
8. Access the API documentation at http://localhost:8000/swagger/

## API Endpoints

- `/api/surveys/` - Survey management
- `/api/questions/` - Question management
- `/api/responses/` - Response management
- `/api/responses/submit/` - Submit a complete survey response
- `/api/departments/` - Department management
- `/api/schedules/` - Survey scheduling
- `/api/analytics/` - Survey analytics

## Cloud Deployment

This application is designed to be cloud-native and can be deployed on AWS, GCP, or Azure. For production deployment, consider:

- Using a production-grade database like PostgreSQL
- Setting up proper environment variables
- Configuring a web server like Nginx with Gunicorn
- Setting up proper SSL/TLS
- Implementing proper backup and monitoring

## Development Journal

Throughout the development process, I leveraged AI tools to accelerate development:

1. **Architecture Planning**: Used AI to help design the initial data models and system architecture
2. **Boilerplate Generation**: Generated initial model structures and API endpoints
3. **Test Case Generation**: Created comprehensive test cases for models and views
4. **Code Refactoring**: Improved code organization and structure
5. **Documentation**: Generated API documentation and README

AI tools significantly reduced development time while maintaining high code quality and comprehensive test coverage.
