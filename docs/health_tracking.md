# Health Tracking System for Hanoi Pet Adoption

This module implements a comprehensive health tracking system for pets, allowing users to:

- Create health records with different record types (general, vaccination, treatment, weight)
- Upload media attachments (photos, videos, documents) to health records
- Set reminders for vaccinations and other health-related activities
- Track pet weight over time
- View health statistics and vaccination history
- View calendar of health events
- Receive notifications for upcoming health activities

## API Endpoints

### Health Records

- `POST /api/health-records`: Create a new health record
- `GET /api/health-records/{record_id}`: Get a specific health record
- `PUT /api/health-records/{record_id}`: Update a health record
- `DELETE /api/health-records/{record_id}`: Delete a health record
- `GET /api/health-records/pet/{pet_id}`: Get all health records for a pet
- `POST /api/health-records/{record_id}/media`: Upload media to a health record
- `POST /api/health-records/{record_id}/media/bulk`: Upload multiple media files to a health record
- `GET /api/health-records/{record_id}/media`: Get all media for a health record
- `DELETE /api/health-records/{record_id}/media/{media_id}`: Delete media from a health record

### Reminders

- `GET /api/reminders/upcoming`: Get upcoming reminders for the current user's pets
- `POST /api/reminders/vaccination`: Create a vaccination reminder

### Health Statistics

- `GET /api/health-stats/pet/{pet_id}/weight-history`: Get weight history for a pet
- `GET /api/health-stats/pet/{pet_id}/summary`: Get summary statistics for a pet's health records
- `GET /api/health-stats/pet/{pet_id}/vaccination-status`: Get vaccination status for a pet
- `GET /api/health-stats/dashboard`: Get comprehensive health dashboard for all user's pets

### Calendar

- `GET /api/calendar/month`: Get a calendar view of health events for a specific month

### Notifications

- `GET /api/notifications`: Get notifications for the current user

### Health Statistics

- `GET /api/health-stats/pet/{pet_id}/weight-history`: Get weight history for a pet
- `GET /api/health-stats/pet/{pet_id}/summary`: Get summary statistics for a pet's health records
- `GET /api/health-stats/pet/{pet_id}/vaccination-status`: Get vaccination status for a pet

## Database Structure

The health tracking system uses the following database tables:

- `health_records`: Stores health record entries with fields for record type, notes, weight, and reminder dates
- `health_record_media`: Stores media attachments for health records

## Usage Examples

### Creating a health record

```python
import requests

# Authorization header with JWT token
headers = {
    "Authorization": "Bearer YOUR_JWT_TOKEN"
}

# Create a general health record
data = {
    "record_type": "general",
    "pet_id": 1,
    "notes": "Annual checkup - all looks good",
    "next_reminder_date": "2024-05-01T10:00:00"
}

response = requests.post(
    "http://localhost:8000/api/health-records",
    json=data,
    headers=headers
)

print(response.json())
```

### Uploading media to a health record

```python
import requests

# Authorization header with JWT token
headers = {
    "Authorization": "Bearer YOUR_JWT_TOKEN"
}

# Upload an image to a health record
files = {
    "file": ("image.jpg", open("path/to/image.jpg", "rb"), "image/jpeg")
}
data = {
    "media_type": "image"
}

response = requests.post(
    "http://localhost:8000/api/health-records/1/media",
    files=files,
    data=data,
    headers=headers
)

print(response.json())
```

### Getting upcoming reminders

```python
import requests

# Authorization header with JWT token
headers = {
    "Authorization": "Bearer YOUR_JWT_TOKEN"
}

# Get reminders for the next 14 days
response = requests.get(
    "http://localhost:8000/api/reminders/upcoming?days_ahead=14",
    headers=headers
)

print(response.json())
```

## Implementation Notes

- Media files are stored in the `uploads/media/health_records/{record_id}` directory
- Proper user authorization is enforced for all operations
- Record types are defined as an enum: `general`, `vaccination`, `treatment`, `weight`
- Media types are defined as an enum: `image`, `video`, `document`
