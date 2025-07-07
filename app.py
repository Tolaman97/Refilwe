from flask import Flask, render_template, redirect, url_for, request, session, flash
import mysql.connector
from datetime import datetime

app = Flask(__name__)
app.secret_key = '12345'

#Create DB and Table on Startup
def init_db():
    conn = mysql.connector.connect(
        host="127.0.0.1",
        user="root",
        password="Tolaman@970927"
    )
    cursor = conn.cursor()
    cursor.execute("CREATE DATABASE IF NOT EXISTS hydroponic_db")
    cursor.execute("USE hydroponic_db")
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS sensor_data (
            id INT AUTO_INCREMENT PRIMARY KEY,
            humidity INT,
            temperature FLOAT,
            motion INT,
            ldr1 INT,
            ldr2 INT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    """)
    conn.commit()
    cursor.close()
    conn.close()

init_db()

#Database Connection
def get_db_connection():
    return mysql.connector.connect(
        host="127.0.0.1",
        user="root",
        password="Tolaman@970927",
        database="hydroponic_db"
    )

#Users and Access Permissions
users = {
    'LEAGO': {'password': '1', 'access': ['humidity']},
    'LUNGILE': {'password': '2', 'access': ['temperature']},
    'REFILWE': {'password': '3', 'access': ['infrared']},
    'ZANELE': {'password': '4', 'access': ['ldr1']},
    'RIJO': {'password': '5', 'access': ['ldr2']},
    'admin': {'password': 'admin', 'access': ['humidity', 'temperature', 'infrared', 'ldr1', 'ldr2']}
}

#Routes
@app.route('/')
def home():
    return render_template('home.html')

@app.route('/about_us')
def about_us():
    return render_template('about_us.html')

@app.route('/contact_us')
def contact_us():
    return render_template('contact_us.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = users.get(username)

        if user and user['password'] == password:
            session['loggedin'] = True
            session['username'] = username
            session['access'] = user['access']
            return redirect(url_for('dashboard'))
        else:
            flash('Incorrect username/password!')
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    flash('You have been logged out.')
    return redirect(url_for('login'))

@app.route('/dashboard')
def dashboard():
    if 'loggedin' in session:
        return render_template('dashboard.html', access=session.get('access', []))
    return redirect(url_for('login'))

@app.route('/sensor/<sensor_type>')
def sensor_data(sensor_type):
    if 'loggedin' not in session:
        return redirect(url_for('login'))

    allowed = session.get('access', [])
    if sensor_type not in allowed:
        return "Unauthorized access.", 403

    query_map = {
        'humidity': "SELECT timestamp, humidity FROM sensor_data ORDER BY timestamp DESC",
        'temperature': "SELECT timestamp, temperature FROM sensor_data ORDER BY timestamp DESC",
        'infrared': "SELECT timestamp, motion FROM sensor_data ORDER BY timestamp DESC",
        'ldr1': "SELECT timestamp, ldr1 FROM sensor_data ORDER BY timestamp DESC",
        'ldr2': "SELECT timestamp, ldr2 FROM sensor_data ORDER BY timestamp DESC"
    }

    if sensor_type in query_map:
        conn = get_db_connection()
        cursor = conn.cursor()
        try:
            cursor.execute(query_map[sensor_type])
            data = cursor.fetchall()
        finally:
            cursor.close()
            conn.close()
        return render_template('sensor_data.html', data=data, sensor_type=sensor_type.capitalize())

    return "Invalid sensor type.", 404

@app.route('/esp32', methods=['POST'])
def esp32_data():
    content = request.json
    humidity = content['humidity']
    temperature = content['temperature']
    motion = content['motion']
    ldr1 = content['ldr1']
    ldr2 = content['ldr2']
    timestamp = datetime.now()

    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("""
            INSERT INTO sensor_data (
                humidity,
                temperature,
                motion,
                ldr1,
                ldr2,
                timestamp
            ) VALUES (%s, %s, %s, %s, %s, %s)
        """, (
            humidity,
            temperature,
            motion,
            ldr1,
            ldr2,
            timestamp
        ))
        conn.commit()
    finally:
        cursor.close()
        conn.close()

    return 'Data Inserted', 200

#Admin Route to View All Sensor Data
@app.route('/all_sensor_data')
def all_sensor_data():
    if 'loggedin' not in session:
        return redirect(url_for('login'))

    if session['username'] != 'admin':
        return "Unauthorized access", 403

    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("""
            SELECT timestamp, humidity, temperature, motion, ldr1, ldr2
            FROM sensor_data
            ORDER BY timestamp DESC
        """)
        data = cursor.fetchall()
    finally:
        cursor.close()
        conn.close()
    return render_template('all_sensor_data.html', data=data)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)



