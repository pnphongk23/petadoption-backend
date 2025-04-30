from alembic.config import Config
from alembic import command
import os
import sys
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Add the parent directory to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

try:
    from app.db.session import Base, engine
    from app.models import *  # Import all models to ensure they're registered with SQLAlchemy
except Exception as e:
    logger.error(f"Error importing modules: {str(e)}")
    print(f"Error: {str(e)}")
    print("This might be due to database connection issues or missing Python packages.")
    print("Make sure you have installed all required packages and configured database access correctly.")
    sys.exit(1)

def setup_alembic():
    """Set up Alembic for database migrations."""
    try:
        # Create versions directory if it doesn't exist
        os.makedirs('alembic/versions', exist_ok=True)
        
        # Check if alembic.ini exists, create if not
        if not os.path.exists("alembic.ini"):
            logger.info("Creating a default alembic.ini file...")
            # Create a basic alembic.ini file with minimal configuration
            with open("alembic.ini", "w") as f:
                f.write("""# A generic, single database configuration.

[alembic]
# path to migration scripts
script_location = alembic

# template used to generate migration files
file_template = %%(rev)s_%%(slug)s

# timezone to use when rendering the date
# within the migration file as well as the filename.
# string value is passed to dateutil.tz.gettz()
# leave blank for localtime
# timezone =

# max length of characters to apply to the
# "slug" field
# truncate_slug_length = 40

# set to 'true' to run the environment during
# the 'revision' command, regardless of autogenerate
# revision_environment = false

# set to 'true' to allow .pyc and .pyo files without
# a source .py file to be detected as revisions in the
# versions/ directory
# sourceless = false

# version location specification; this defaults
# to alembic/versions.  When using multiple version
# directories, initial revisions must be specified with --version-path
# version_locations = %(here)s/bar %(here)s/bat alembic/versions

# the output encoding used when revision files
# are written from script.py.mako
# output_encoding = utf-8

sqlalchemy.url = {engine.url}

[post_write_hooks]

# Logging configuration
[loggers]
keys = root,sqlalchemy,alembic

[handlers]
keys = console

[formatters]
keys = generic

[logger_root]
level = WARN
handlers = console
qualname =

[logger_sqlalchemy]
level = WARN
handlers =
qualname = sqlalchemy.engine

[logger_alembic]
level = INFO
handlers =
qualname = alembic

[handler_console]
class = StreamHandler
args = (sys.stderr,)
level = NOTSET
formatter = generic

[formatter_generic]
format = %(levelname)-5.5s [%(name)s] %(message)s
datefmt = %H:%M:%S
""".format(engine=engine))

        # Create Alembic configuration
        logger.info("Loading Alembic configuration...")
        alembic_cfg = Config("alembic.ini")
        
        # Create or update Alembic migration environment
        logger.info("Initializing Alembic environment...")
        command.init(alembic_cfg, 'alembic')
        
        # Auto-generate a migration based on the current models
        logger.info("Creating initial migration...")
        command.revision(alembic_cfg, autogenerate=True, message="Initial migration")
        
        # Apply the migration to the database
        logger.info("Applying migrations to database...")
        command.upgrade(alembic_cfg, "head")
        
        logger.info("Successfully set up Alembic and created initial migration.")
        print("Successfully set up Alembic and created initial migration.")
        return True
    except Exception as e:
        logger.error(f"Error setting up Alembic: {str(e)}")
        print(f"Error setting up Alembic: {str(e)}")
        return False

def create_tables():
    """Create all tables defined in the models."""
    try:
        # Test database connection first
        logger.info("Testing database connection...")
        connection = engine.connect()
        connection.close()
        logger.info("Database connection successful")
        
        # Create all tables
        logger.info("Creating database tables...")
        Base.metadata.create_all(bind=engine)
        logger.info("Successfully created database tables.")
        print("Successfully created database tables.")
        return True
    except Exception as e:
        logger.error(f"Error creating tables: {str(e)}")
        print(f"Error creating tables: {str(e)}")
        print("\nPossible solutions:")
        print("1. Make sure MySQL server is running")
        print("2. Check database credentials in app/config.py or .env file")
        print("3. If using mysqlclient and getting build errors:")
        print("   a. Install Microsoft C++ Build Tools")
        print("   b. Or use pymysql instead by modifying app/config.py:")
        print("      Change DATABASE_URL to use 'mysql+pymysql://' instead of 'mysql://'")
        print("      And run: pip install pymysql")
        return False

if __name__ == "__main__":
    # Create tables directly using SQLAlchemy
    create_tables()
    
    # Set up Alembic for future migrations
    setup_alembic()
