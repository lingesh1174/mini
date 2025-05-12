from flask import Flask, request, jsonify, render_template, redirect, url_for, session
import mysql.connector
from mysql.connector import Error
from datetime import datetime
import os

app = Flask(__name__)
app.secret_key = 'your_secret_key'
UPLOAD_FOLDER = 'uploads/'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

host = 'localhost'
user = 'root'
password = 'Nagasrinivas@11'
database = 'hospital_db'

os.makedirs(UPLOAD_FOLDER, exist_ok=True)

def get_db_connection():
    try:
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

def initialize_db():
    try:
        conn = mysql.connector.connect(
            host=host,
            user=user,
            password=password
        )
        if conn.is_connected():
            cursor = conn.cursor()
            cursor.execute(f"CREATE DATABASE IF NOT EXISTS {database}")
            cursor.execute(f"USE {database}")
            cursor.execute(''' 
            CREATE TABLE IF NOT EXISTS datatable (
                id INT AUTO_INCREMENT PRIMARY KEY,
                complaint_title VARCHAR(255) NOT NULL,
                complaint_description TEXT NOT NULL,
                complaint_against VARCHAR(255) NOT NULL,
                hospital_name VARCHAR(255) NOT NULL,
                hospital_location VARCHAR(255) NOT NULL,
                complainant_name VARCHAR(255) NOT NULL,
                email VARCHAR(255) NOT NULL,
                phone VARCHAR(15) NOT NULL,
                aadhar VARCHAR(12) NOT NULL,
                complaint_date DATE NOT NULL,
                complaint_photo VARCHAR(255)
            )
            ''')
            cursor.execute(''' 
            CREATE TABLE IF NOT EXISTS orders (
                id INT AUTO_INCREMENT PRIMARY KEY,
                hospital_name VARCHAR(255),
                hospital_location VARCHAR(255),
                orderer_name VARCHAR(255),
                order_date DATETIME,
                cart_items TEXT
            )
            ''')
            print("Database and tables created successfully.")
            cursor.close()
            conn.close()
    except Error as e:
        print(f"Error initializing database: {e}")

@app.route('/')
def login():
    return render_template('login.html')


@app.route('/login', methods=['POST'])
def login_user():
    username = request.form.get('username')
    password = request.form.get('password')

    if username == 'admin' and password == 'password':
        session['user'] = username
        return redirect(url_for('home'))
    else:
        return render_template('login.html', error="Invalid credentials")


@app.route('/logout')
def logout():
    session.pop('user', None)
    return redirect(url_for('login'))


@app.route('/home')
def home():
    if 'user' not in session:
        return redirect(url_for('login'))
    return render_template('home.html')


@app.route('/complaint')
def index():
    if 'user' not in session:
        return redirect(url_for('login'))
    return render_template('index.html')


@app.route('/register', methods=['POST'])
def register_complaint():
    if 'user' not in session:
        return redirect(url_for('login'))

    complaint_title = request.form['complaint_title']
    complaint_description = request.form['complaint_description']
    complaint_against = request.form['complaint_against']
    hospital_name = request.form['hospital_name']
    hospital_location = request.form['hospital_location']
    complainant_name = request.form['complainant_name']
    email = request.form['email']
    phone = request.form['phone']
    aadhar = request.form['aadhar']
    complaint_date = request.form['complaint_date']

    complaint_photo = request.files.get('complaint_photo')
    photo_filename = None
    if complaint_photo:
        photo_filename = os.path.join(app.config['UPLOAD_FOLDER'], complaint_photo.filename)
        complaint_photo.save(photo_filename)

    conn = get_db_connection()

    if conn:
        try:
            cursor = conn.cursor()
            cursor.execute(''' 
                INSERT INTO datatable (
                    complaint_title, complaint_description, complaint_against, 
                    hospital_name, hospital_location, complainant_name, email, 
                    phone, aadhar, complaint_date, complaint_photo
                )
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            ''', (
                complaint_title, complaint_description, complaint_against,
                hospital_name, hospital_location, complainant_name, email,
                phone, aadhar, complaint_date, photo_filename
            ))
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
    if 'user' not in session:
        return redirect(url_for('login'))

    conn = get_db_connection()

    if conn:
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM datatable")
            complaints = cursor.fetchall()

            return render_template('complaints.html', complaints=complaints)
        except Error as e:
            return f"Database error: {e}"
        finally:
            if conn.is_connected():
                cursor.close()
                conn.close()

    return "Unable to connect to the database."


@app.route('/requirements')
def requirements():
    if 'user' not in session:
        return redirect(url_for('login'))
    return render_template('requirement.html')


@app.route('/submit_order', methods=['POST'])
def submit_order():
    if 'user' not in session:
        return redirect(url_for('login'))

    try:
        data = request.get_json()
        hospital_name = data.get('hospitalName')
        hospital_location = data.get('hospitalLocation')
        orderer_name = data.get('ordererName')
        cart_items = data.get('cartItems')

        if not cart_items:
            return jsonify({'error': 'Cart is empty'}), 400

        order_date = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute(""" 
            INSERT INTO orders (hospital_name, hospital_location, orderer_name, order_date, cart_items)
            VALUES (%s, %s, %s, %s, %s)
        """, (hospital_name, hospital_location, orderer_name, order_date, str(cart_items)))

        conn.commit()

        cursor.close()
        conn.close()

        return jsonify({'message': 'Order submitted successfully!'}), 200

    except Error as e:
        return jsonify({'error': str(e)}), 500


if __name__ == '__main__':
    initialize_db()
    app.run(debug=True)
