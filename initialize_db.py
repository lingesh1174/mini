import mysql.connector
from mysql.connector import Error

# MySQL connection parameters
host = 'localhost'
user = 'root'
password = 'Nagasrinivas@11'
database = 'hospital_db'  # Name of your database

try:
    # Connect to MySQL database
    conn = mysql.connector.connect(
        host=host,
        user=user,
        password=password
    )

    if conn.is_connected():
        print("Connected to MySQL server")

        # Create the database if it doesn't exist
        cursor = conn.cursor()
        cursor.execute(f"CREATE DATABASE IF NOT EXISTS {database}")
        cursor.execute(f"USE {database}")

        # Create the patients table if it doesn't exist
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS patients (
            id INT AUTO_INCREMENT PRIMARY KEY,
            name VARCHAR(100) NOT NULL,
            age INT NOT NULL,
            gender VARCHAR(10) NOT NULL,
            contact VARCHAR(15) NOT NULL,
            medical_history TEXT NOT NULL
        )
        ''')

        print("Database and table created successfully.")

except Error as e:
    print(f"Error: {e}")
finally:
    if conn.is_connected():
        cursor.close()
        conn.close()
