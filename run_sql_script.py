import mysql.connector
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Get MySQL credentials from .env file
mysql_user = os.getenv("MYSQL_USER", "root")
mysql_password = os.getenv("MYSQL_PASSWORD", "root")  # Using the password you set in .env
mysql_host = os.getenv("MYSQL_SERVER", "localhost")
mysql_port = int(os.getenv("MYSQL_PORT", "3306"))

print(f"Attempting to connect to MySQL with:")
print(f"Host: {mysql_host}")
print(f"User: {mysql_user}")
print(f"Port: {mysql_port}")
print(f"Password: {'*' * len(mysql_password) if mysql_password else '(empty)'}")

try:
    # Create a connection using the parameters from your .env file
    conn = mysql.connector.connect(
        host=mysql_host,
        user=mysql_user,
        password=mysql_password,
        port=mysql_port
    )
    
    if conn.is_connected():
        print("Successfully connected to MySQL server!")
        db_info = conn.get_server_info()
        print(f"MySQL server version: {db_info}")
        
        # Read the SQL script
        with open("setup_database.sql", "r") as sql_file:
            sql_script = sql_file.read()
            
        # Execute the SQL script - splitting by semicolons
        cursor = conn.cursor()
        
        # MySQL doesn't support executing multiple statements at once through connector
        # So we split the script and execute each statement separately
        for statement in sql_script.split(';'):
            if statement.strip():  # Skip empty statements
                print(f"Executing: {statement[:50]}...")  # Print first 50 chars for logging
                cursor.execute(statement)
                
        print("SQL script executed successfully!")
        conn.commit()  # Commit the changes
        
        # Close the connection
        cursor.close()
        conn.close()
        print("Connection closed")
except mysql.connector.Error as err:
    print(f"Error with MySQL: {err}")
    
    # Provide troubleshooting guidance based on error
    if "Can't connect to MySQL server" in str(err):
        print("\nTroubleshooting suggestions:")
        print("1. Make sure MySQL server is running")
        print("2. Check if MySQL is installed correctly")
        print("3. Verify MySQL is listening on default port 3306")
    elif "Access denied" in str(err):
        print("\nTroubleshooting suggestions:")
        print("1. Check your MySQL username and password")
        print("2. Try a different password")
    elif "You have an error in your SQL syntax" in str(err):
        print("\nSQL syntax error detected. Check your SQL script for errors.")
