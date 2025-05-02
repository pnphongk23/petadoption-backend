# filepath: e:\Git\hanoitpetpython\app\db\base_class.py
from sqlalchemy.ext.declarative import declarative_base

# Create Base class for SQLAlchemy models
Base = declarative_base()

# We define Base here to avoid circular imports
# This approach keeps model definitions separate from session creation
