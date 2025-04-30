# Models package
# Define which model classes should be available when importing from app.models
__all__ = ["User", "Pet", "OTP"]

# Import the classes at the end to avoid circular imports
from app.models.user import User
# Don't directly import - allow classes to be loaded when needed
# from app.models.pet import Pet
# from app.models.otp import OTP
