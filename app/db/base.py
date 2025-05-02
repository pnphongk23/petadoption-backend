# filepath: e:\Git\hanoitpetpython\app\db\base.py
# Import all models here for Alembic to detect them
from app.db.base_class import Base

# Import all models
from app.models.user import User
from app.models.pet import Pet
from app.models.health_record import HealthRecord
from app.models.health_record_media import HealthRecordMedia

# Import additional models as needed
