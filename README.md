# Hanoi Pet Adoption Backend API

A FastAPI-based backend for the Hanoi Pet Adoption application, providing APIs for pet adoption, user management, and health tracking features.

## Features

- **User Authentication**: JWT-based authentication system
- **Pet Management**: Create, update, and search for pets available for adoption
- **Adoption Process**: Manage adoption requests and status
- **Health Tracking System**: 
  - Record pet health information
  - Upload photos and videos
  - Set vaccination reminders
  - Track weight and other metrics
  - View health statistics
  - Calendar view of health events
  - Notifications for upcoming health activities
  - Health dashboard with comprehensive information

## Getting Started

### Prerequisites

- Python 3.10+ (developed with Python 3.12)
- MySQL 8.0+

### Installation

1. Clone the repository
   ```bash
   git clone https://github.com/yourusername/hanoitpetpython.git
   cd hanoitpetpython
   ```

2. Create and activate a virtual environment
   ```bash
   python -m venv venv
   .\venv\Scripts\activate  # On Windows
   ```

3. Install dependencies
   ```bash
   pip install -r requirements.txt
   ```

4. Create a `.env` file with your configuration
   ```
   MYSQL_USER=your_mysql_user
   MYSQL_PASSWORD=your_mysql_password
   MYSQL_SERVER=localhost
   MYSQL_PORT=3306
   MYSQL_DB=pet_adoption_db
   SECRET_KEY=your_secret_key
   ```

5. Initialize the database
   ```bash
   python setup_database.py
   ```

6. Run the setup script for the health tracking feature
   ```bash
   python setup_health_tracking.py
   ```
   
   This script will:
   - Run database migrations
   - Set up media directories
   - Check for required dependencies

7. Start the server
   ```bash
   python main.py
   ```

The API will be available at http://localhost:8000

## API Documentation

When the application is running, you can access:
- Swagger UI documentation: http://localhost:8000/api/docs
- ReDoc documentation: http://localhost:8000/api/redoc

## Health Tracking Module

The health tracking feature allows pet owners to:

- Create different types of health records (general, vaccination, treatment, weight)
- Upload images and videos as attachments to health records
- Set and receive reminders for vaccinations and other health events
- View statistics and trends in pet health

For detailed documentation about the health tracking API, see [docs/health_tracking.md](docs/health_tracking.md)

## Running Tests

```bash
pytest
```

To run specific tests with verbose output:

```bash
pytest tests/test_health_records.py -v
```

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgements

- [FastAPI](https://fastapi.tiangolo.com/)
- [SQLAlchemy](https://www.sqlalchemy.org/)
- [Alembic](https://alembic.sqlalchemy.org/)
- [Pydantic](https://pydantic-docs.helpmanual.io/)
