from flask import Flask, render_template, request, redirect, url_for
import mysql.connector
from mysql.connector import Error
import os

app = Flask(__name__)

# Set the folder for file uploads
UPLOAD_FOLDER = 'uploads/'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# MySQL connection parameters
host = 'localhost'
user = 'root'
password = 'Nagasrinivas@11'
database = 'hospital_db'

# Ensure the upload folder exists
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Function to connect to MySQL database
def get_db_connection():
    try:
        # Establish connection to MySQL
        conn = mysql.connector.connect(
            host=host,
            user=user,
            password=password,
            database=database
        )
        if conn.is_connected():
            return conn
        else:
            return None
    except Error as e:
        print(f"Error: {e}")
        return None

# Function to initialize the database and table
def initialize_db():
    try:
        # Connect to MySQL server (without database)
        conn = mysql.connector.connect(
            host=host,
            user=user,
            password=password
        )
        if conn.is_connected():
            print("Connected to MySQL server")

            cursor = conn.cursor()
            # Create the database if it doesn't exist
            cursor.execute(f"CREATE DATABASE IF NOT EXISTS {database}")
            cursor.execute(f"USE {database}")

            # Create the complaintregister table if it doesn't exist
            cursor.execute('''
            CREATE TABLE IF NOT EXISTS complaintregister (
                id INT AUTO_INCREMENT PRIMARY KEY,
                complaint_title VARCHAR(255) NOT NULL,
                complaint_description TEXT NOT NULL,
                complainant_name VARCHAR(255) NOT NULL,
                email VARCHAR(255) NOT NULL,
                phone VARCHAR(15) NOT NULL,
                aadhar VARCHAR(12) NOT NULL,  -- Aadhar field
                complaint_date DATE NOT NULL,
                complaint_photo VARCHAR(255)  -- Path to the uploaded photo
            )
            ''')

            print("Database and table created successfully.")
            cursor.close()
            conn.close()
    except Error as e:
        print(f"Error initializing database: {e}")

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/register', methods=['POST'])
def register_complaint():
    complaint_title = request.form['complaint_title']
    complaint_description = request.form['complaint_description']
    complainant_name = request.form['complainant_name']
    email = request.form['email']
    phone = request.form['phone']
    aadhar = request.form['aadhar']
    complaint_date = request.form['complaint_date']

    # Handle photo upload
    complaint_photo = request.files.get('complaint_photo')
    photo_filename = None
    if complaint_photo:
        # Save the photo to the server
        photo_filename = os.path.join(app.config['UPLOAD_FOLDER'], complaint_photo.filename)
        complaint_photo.save(photo_filename)

    # Connect to MySQL database
    conn = get_db_connection()

    if conn:
        try:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO complaintregister (complaint_title, complaint_description, complainant_name, email, phone, aadhar, complaint_date, complaint_photo)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            ''', (complaint_title, complaint_description, complainant_name, email, phone, aadhar, complaint_date, photo_filename))
            conn.commit()
            return redirect(url_for('view_complaints'))
        except Error as e:
            return f"Database error: {e}"
        finally:
            if conn.is_connected():
                cursor.close()
                conn.close()

    return "Unable to connect to the database."

@app.route('/complaints')
def view_complaints():
    conn = get_db_connection()

    if conn:
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM complaintregister")
            complaints = cursor.fetchall()  # Fetch all rows

            return render_template('complaints.html', complaints=complaints)
        except Error as e:
            return f"Database error: {e}"
        finally:
            if conn.is_connected():
                cursor.close()
                conn.close()

    return "Unable to connect to the database."

if __name__ == '__main__':
    # Initialize the database and table when the app starts
    initialize_db()
    app.run(debug=True)
