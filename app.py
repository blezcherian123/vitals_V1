from flask import Flask, render_template, request, jsonify, flash, redirect, url_for
import mysql.connector
from config import Config
from ai_module import AIModule
import pandas as pd
from datetime import datetime
import json

app = Flask(__name__)
app.secret_key = 'your-secret-key-here'  # Change this to a secure secret key
ai = AIModule()

# Database connection
def get_db_connection():
    try:
        return mysql.connector.connect(
            host=Config.MYSQL_HOST,
            user=Config.MYSQL_USER,
            password=Config.MYSQL_PASSWORD,
            database=Config.MYSQL_DB
        )
    except mysql.connector.Error as err:
        print(f"Database connection error: {err}")
        return None

# Initialize database tables
def init_db():
    conn = get_db_connection()
    if conn:
        cursor = conn.cursor()
        try:
            # Create vital_signs table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS vital_signs (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    registration_id VARCHAR(50) NOT NULL,
                    name VARCHAR(100) NOT NULL,
                    gender ENUM('MALE', 'FEMALE') NOT NULL,
                    age INT NOT NULL,
                    date DATE NOT NULL,
                    time TIME NOT NULL,
                    height FLOAT NOT NULL,
                    weight FLOAT NOT NULL,
                    bmi FLOAT NOT NULL,
                    temp FLOAT NOT NULL,
                    systolic_bp INT NOT NULL,
                    diastolic_bp INT NOT NULL,
                    pulse INT NOT NULL,
                    pain_scale INT NOT NULL,
                    summary TEXT NOT NULL,
                    alerts TEXT NOT NULL,
                    recommendations TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Create patients table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS patients (
                    registration_id VARCHAR(50) PRIMARY KEY,
                    name VARCHAR(100) NOT NULL,
                    gender ENUM('MALE', 'FEMALE') NOT NULL,
                    age INT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            conn.commit()
        except mysql.connector.Error as err:
            print(f"Error creating tables: {err}")
        finally:
            cursor.close()
            conn.close()

# Initialize database on startup
init_db()

# Load and train ML model (optional for MVP)
# ai.train_ml_model('vital_signs_disease_dataset_1000.xlsx')

@app.route('/')
def index():
    return render_template('nurse_dashboard.html')

@app.route('/doctor')
def doctor_dashboard():
    try:
        conn = get_db_connection()
        if not conn:
            flash('Database connection error', 'error')
            return render_template('doctor_dashboard.html', patients=[])
            
        cursor = conn.cursor(dictionary=True)
        
        # Get latest vital signs for each patient
        cursor.execute('''
            SELECT v.*, p.name, p.gender, p.age
            FROM vital_signs v
            JOIN patients p ON v.registration_id = p.registration_id
            WHERE v.created_at IN (
                SELECT MAX(created_at)
                FROM vital_signs
                GROUP BY registration_id
            )
            ORDER BY v.created_at DESC
        ''')
        
        patients = cursor.fetchall()
        
        # Process patient data for display
        for patient in patients:
            patient['alerts'] = patient['alerts'].split('; ')
            patient['recommendations'] = patient['recommendations'].split('; ')
            
        cursor.close()
        conn.close()
        
        return render_template('doctor_dashboard.html', patients=patients)
    except Exception as e:
        flash(f'Error loading dashboard: {str(e)}', 'error')
        return render_template('doctor_dashboard.html', patients=[])

@app.route('/submit_vitals', methods=['POST'])
def submit_vitals():
    try:
        data = request.json
        
        # Validate required fields
        required_fields = ['registration_id', 'name', 'gender', 'age', 'height', 'weight', 
                         'temp', 'systolic_bp', 'diastolic_bp', 'pulse', 'pain_scale']
        for field in required_fields:
            if field not in data or not data[field]:
                return jsonify({'error': f'Missing required field: {field}'}), 400
        
        # Calculate BMI and generate analysis
        bmi = ai.calculate_bmi(data['height'], data['weight'])
        summary = ai.generate_summary(data)
        alerts = ai.generate_alerts(data)
        recommendations = ai.generate_recommendations(data)
        
        # Store in database
        conn = get_db_connection()
        if not conn:
            return jsonify({'error': 'Database connection error'}), 500
            
        cursor = conn.cursor()
        
        try:
            # Insert or update patient record
            cursor.execute('''
                INSERT INTO patients (registration_id, name, gender, age)
                VALUES (%s, %s, %s, %s)
                ON DUPLICATE KEY UPDATE
                name = VALUES(name),
                gender = VALUES(gender),
                age = VALUES(age)
            ''', (data['registration_id'], data['name'], data['gender'], data['age']))
            
            # Insert vital signs
            cursor.execute('''
                INSERT INTO vital_signs (
                    registration_id, name, gender, age, date, time,
                    height, weight, bmi, temp, systolic_bp, diastolic_bp,
                    pulse, pain_scale, summary, alerts, recommendations
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            ''', (
                data['registration_id'], data['name'], data['gender'], data['age'],
                data['date'], data['time'], data['height'], data['weight'],
                bmi, data['temp'], data['systolic_bp'], data['diastolic_bp'],
                data['pulse'], data['pain_scale'], summary,
                '; '.join(alerts), '; '.join(recommendations)
            ))
            
            conn.commit()
            
            return jsonify({
                'bmi': bmi,
                'summary': summary,
                'alerts': alerts,
                'recommendations': recommendations
            })
            
        except mysql.connector.Error as err:
            conn.rollback()
            return jsonify({'error': f'Database error: {str(err)}'}), 500
        finally:
            cursor.close()
            conn.close()
            
    except Exception as e:
        return jsonify({'error': f'Server error: {str(e)}'}), 500

@app.route('/patient_history/<registration_id>')
def patient_history(registration_id):
    try:
        conn = get_db_connection()
        if not conn:
            return jsonify({'error': 'Database connection error'}), 500
            
        cursor = conn.cursor(dictionary=True)
        cursor.execute('''
            SELECT * FROM vital_signs
            WHERE registration_id = %s
            ORDER BY created_at DESC
        ''', (registration_id,))
        
        history = cursor.fetchall()
        cursor.close()
        conn.close()
        
        return jsonify(history)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)