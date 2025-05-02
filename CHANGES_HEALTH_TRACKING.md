# Health Tracking Feature Implementation

## Overview

This implementation introduces a comprehensive health tracking system for the Hanoi Pet Adoption application. 
The feature allows users to maintain detailed health records for their pets, including the ability to 
upload photos and videos, set reminders for vaccinations and treatments, and view health statistics over time.
It also provides a calendar view for health events and a notification system for upcoming activities.

## Changes Made

### Database Models

- Added `HealthRecord` model to store health record information (record type, notes, weight)
- Added `HealthRecordMedia` model to store media attachments (images, videos, documents)
- Updated `Pet` and `User` models with relationships to health records

### API Endpoints

Added the following API endpoints:

- Health Records API (`/api/health-records/*`)
- Reminders API (`/api/reminders/*`)
- Health Statistics API (`/api/health-stats/*`)
- Calendar API (`/api/calendar/*`)
- Notifications API (`/api/notifications`)

### Services

- Health Record Service: Manages CRUD operations for health records
- Health Record Media Service: Handles media attachments
- Reminder Service: Handles vaccination and health reminders
- Health Stats Service: Provides statistics and summaries
- Calendar Service: Provides calendar views of health events
- Notification Service: Manages user notifications for health activities

### Utilities

- File Storage: Manages uploading and retrieving media files
- Pet Ownership: Verifies user's permission to access a pet's records

### Documentation

- Added detailed documentation for the health tracking feature
- Updated Swagger/OpenAPI documentation

### Testing

- Added unit tests for health record endpoints
- Created test fixtures for testing database operations

### Other

- Added migration script for the new database tables
- Created initialization script for media storage directories
- Updated requirements.txt with testing dependencies

## How to Run Migrations

```
python scripts/run_migrations.py
```

## How to Initialize Media Directories

```
python scripts/initialize_media.py
```

## Testing

```
pytest tests/test_health_records.py -v
```

## API Usage Examples

See `docs/health_tracking.md` for detailed API usage examples.
