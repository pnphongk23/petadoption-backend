import mysql.connector
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Get MySQL credentials from .env file
mysql_user = os.getenv("MYSQL_USER", "root")
mysql_password = os.getenv("MYSQL_PASSWORD", "")
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
        
        # Try to create the database if it doesn't exist
        cursor = conn.cursor()
        cursor.execute("CREATE DATABASE IF NOT EXISTS pet_adoption_db")
        print("Database 'pet_adoption_db' created or already exists")
        
        # Close the connection
        cursor.close()
        conn.close()
        print("Connection closed")
except mysql.connector.Error as err:
    print(f"Error connecting to MySQL: {err}")
    
    # Provide troubleshooting guidance based on error
    if "Can't connect to MySQL server" in str(err):
        print("\nTroubleshooting suggestions:")
        print("1. Make sure MySQL server is running")
        print("2. Check if MySQL is installed correctly")
        print("3. Verify MySQL is listening on default port 3306")
    elif "Access denied" in str(err):
        print("\nTroubleshooting suggestions:")
        print("1. Check your MySQL username and password")
        print("2. You might need to use a password other than empty string")
