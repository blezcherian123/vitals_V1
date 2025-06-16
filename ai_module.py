import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
from datetime import datetime

class AIModule:
    def __init__(self):
        # Enhanced BMI ranges with more detailed categories
        self.bmi_ranges = {
            'Severely Underweight': (0, 16),
            'Underweight': (16, 18.5),
            'Normal': (18.5, 24.9),
            'Overweight': (25, 29.9),
            'Obesity Class I': (30, 34.9),
            'Obesity Class II': (35, 39.9),
            'Obesity Class III': (40, float('inf'))
        }
        
        # Enhanced BP ranges based on latest guidelines
        self.bp_ranges = {
            'Normal': (0, 120, 0, 80),
            'Elevated': (120, 129, 0, 80),
            'Hypertension Stage 1': (130, 139, 80, 89),
            'Hypertension Stage 2': (140, float('inf'), 90, float('inf')),
            'Hypertensive Crisis': (180, float('inf'), 120, float('inf')),
            'Hypotension': (0, 90, 0, 60)
        }
        
        # Enhanced temperature ranges
        self.temp_ranges = {
            'Hypothermia': (0, 95),
            'Low Normal': (95, 97),
            'Normal': (97, 99),
            'Low Grade Fever': (99, 100.4),
            'Fever': (100.4, 103),
            'High Fever': (103, float('inf'))
        }
        
        # Enhanced pulse ranges with age considerations
        self.pulse_ranges = {
            'Bradycardia': (0, 60),
            'Normal': (60, 100),
            'Tachycardia': (100, float('inf'))
        }
        
        # Initialize ML components
        self.model = None
        self.label_encoder = LabelEncoder()
        self.risk_factors = set()

    def calculate_bmi(self, height_cm, weight_kg):
        height_m = height_cm / 100
        bmi = weight_kg / (height_m ** 2)
        return round(bmi, 1)

    def get_bmi_category(self, bmi):
        for category, (low, high) in self.bmi_ranges.items():
            if low <= bmi < high:
                return category
        return 'Unknown'

    def analyze_bp(self, systolic, diastolic, age):
        # Age-adjusted BP analysis
        if age >= 65:
            # Adjusted ranges for elderly
            if systolic < 120 and diastolic < 70:
                return 'Low Normal for Age'
        
        for category, (s_low, s_high, d_low, d_high) in self.bp_ranges.items():
            if s_low <= systolic < s_high and d_low <= diastolic < d_high:
                return category
        return 'Hypertension Stage 2'

    def analyze_temp(self, temp_f):
        for category, (low, high) in self.temp_ranges.items():
            if low <= temp_f < high:
                return category
        return 'Unknown'

    def analyze_pulse(self, pulse, age):
        # Age-adjusted pulse analysis
        if age < 1:
            normal_range = (120, 160)
        elif age < 3:
            normal_range = (80, 130)
        elif age < 7:
            normal_range = (70, 120)
        elif age < 12:
            normal_range = (60, 100)
        else:
            normal_range = (60, 100)
            
        if pulse < normal_range[0]:
            return 'Bradycardia'
        elif pulse > normal_range[1]:
            return 'Tachycardia'
        return 'Normal'

    def generate_summary(self, patient_data):
        bmi = self.calculate_bmi(patient_data['height'], patient_data['weight'])
        bmi_category = self.get_bmi_category(bmi)
        bp_category = self.analyze_bp(patient_data['systolic_bp'], patient_data['diastolic_bp'], patient_data['age'])
        temp_category = self.analyze_temp(patient_data['temp'])
        pulse_category = self.analyze_pulse(patient_data['pulse'], patient_data['age'])

        # Get recommendations for each vital
        bmi_rec = ''
        if bmi_category in ['Severely Underweight', 'Underweight']:
            bmi_rec = '→ Immediate nutritional assessment required. Consider referral to dietitian.'
        elif bmi_category in ['Obesity Class II', 'Obesity Class III']:
            bmi_rec = '→ Comprehensive weight management program recommended. Screen for diabetes and cardiovascular risk.'

        bp_rec = ''
        if bp_category in ['Hypertension Stage 1', 'Hypertension Stage 2']:
            bp_rec = '→ Lifestyle modifications recommended. Monitor BP twice daily. Consider medication review.'
        elif bp_category == 'Hypotension':
            bp_rec = '→ Increase fluid intake. Review medications. Monitor for dizziness.'
        elif bp_category in ['Hypertensive Crisis']:
            bp_rec = '→ Immediate medical attention required.'

        temp_rec = ''
        if temp_category in ['High Fever', 'Fever']:
            temp_rec = '→ Monitor temperature every 4 hours. Consider antipyretics. Screen for infection.'
        elif temp_category == 'Hypothermia':
            temp_rec = '→ Gradual warming required. Monitor core temperature. Check for underlying causes.'

        pulse_rec = ''
        if pulse_category == 'Bradycardia':
            pulse_rec = '→ Monitor for symptoms of fatigue. Review medications. Consider ECG.'
        elif pulse_category == 'Tachycardia':
            pulse_rec = '→ Monitor for palpitations. Check for underlying causes. Consider stress reduction techniques.'

        summary_lines = [
            f"Patient Summary for {patient_data['name']} (Age: {patient_data['age']}, Gender: {patient_data['gender']}):",
            f"- BMI: {bmi} ({bmi_category}) {bmi_rec}",
            f"- Blood Pressure: {patient_data['systolic_bp']}/{patient_data['diastolic_bp']} mmHg ({bp_category}) {bp_rec}",
            f"- Body Temperature: {patient_data['temp']}°F ({temp_category}) {temp_rec}",
            f"- Pulse Rate: {patient_data['pulse']} bpm ({pulse_category}) {pulse_rec}"
        ]
        return '\n'.join(summary_lines)

    def generate_alerts(self, patient_data):
        alerts = []
        bmi = self.calculate_bmi(patient_data['height'], patient_data['weight'])
        bmi_category = self.get_bmi_category(bmi)
        bp_category = self.analyze_bp(patient_data['systolic_bp'], patient_data['diastolic_bp'], patient_data['age'])
        temp_category = self.analyze_temp(patient_data['temp'])
        pulse_category = self.analyze_pulse(patient_data['pulse'], patient_data['age'])

        # BMI Alerts
        if bmi_category in ['Severely Underweight', 'Underweight']:
            alerts.append(f"Critical Alert: {bmi_category} BMI detected - Immediate nutritional intervention required")
        elif bmi_category in ['Obesity Class II', 'Obesity Class III']:
            alerts.append(f"Critical Alert: {bmi_category} BMI detected - High risk of comorbidities")

        # BP Alerts
        if bp_category in ['Hypertension Stage 2', 'Hypertensive Crisis']:
            alerts.append(f"Critical Alert: {bp_category} detected - Immediate medical attention required")
        elif bp_category == 'Hypotension':
            alerts.append(f"Alert: {bp_category} detected - Monitor for symptoms")

        # Temperature Alerts
        if temp_category in ['High Fever', 'Fever']:
            alerts.append(f"Critical Alert: {temp_category} detected - Possible infection")
        elif temp_category == 'Hypothermia':
            alerts.append(f"Critical Alert: {temp_category} detected - Immediate warming required")

        # Pulse Alerts
        if pulse_category in ['Bradycardia', 'Tachycardia']:
            alerts.append(f"Alert: {pulse_category} detected - Monitor for symptoms")

        return alerts

    def generate_recommendations(self, patient_data):
        recommendations = []
        bmi = self.calculate_bmi(patient_data['height'], patient_data['weight'])
        bmi_category = self.get_bmi_category(bmi)
        bp_category = self.analyze_bp(patient_data['systolic_bp'], patient_data['diastolic_bp'], patient_data['age'])
        temp_category = self.analyze_temp(patient_data['temp'])
        pulse_category = self.analyze_pulse(patient_data['pulse'], patient_data['age'])

        # BMI Recommendations
        if bmi_category in ['Severely Underweight', 'Underweight']:
            recommendations.append("Immediate nutritional assessment required. Consider referral to dietitian.")
        elif bmi_category in ['Obesity Class II', 'Obesity Class III']:
            recommendations.append("Comprehensive weight management program recommended. Screen for diabetes and cardiovascular risk.")

        # BP Recommendations
        if bp_category in ['Hypertension Stage 1', 'Hypertension Stage 2']:
            recommendations.append("Lifestyle modifications recommended. Monitor BP twice daily. Consider medication review.")
        elif bp_category == 'Hypotension':
            recommendations.append("Increase fluid intake. Review medications. Monitor for dizziness.")

        # Temperature Recommendations
        if temp_category in ['High Fever', 'Fever']:
            recommendations.append("Monitor temperature every 4 hours. Consider antipyretics. Screen for infection.")
        elif temp_category == 'Hypothermia':
            recommendations.append("Gradual warming required. Monitor core temperature. Check for underlying causes.")

        # Pulse Recommendations
        if pulse_category == 'Bradycardia':
            recommendations.append("Monitor for symptoms of fatigue. Review medications. Consider ECG.")
        elif pulse_category == 'Tachycardia':
            recommendations.append("Monitor for palpitations. Check for underlying causes. Consider stress reduction techniques.")

        return recommendations

    def train_ml_model(self, data_path):
        try:
            df = pd.read_excel("D:\REACT PROJECT\EMR MVP\patient_dashboard\vital_signs_disease_dataset_1000.xlsx")
            features = ['bmi', 'temp', 'systolic_bp', 'diastolic_bp', 'pulse', 'age']
            X = df[features]
            y = self.label_encoder.fit_transform(df['disease'])

            X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
            self.model = RandomForestClassifier(n_estimators=200, max_depth=10, random_state=42)
            self.model.fit(X_train, y_train)
            
            # Calculate feature importance
            feature_importance = pd.DataFrame({
                'feature': features,
                'importance': self.model.feature_importances_
            }).sort_values('importance', ascending=False)
            
            return feature_importance
        except Exception as e:
            print(f"Error training model: {str(e)}")
            return None

    def predict_disease(self, patient_data):
        if not self.model:
            return "ML model not trained."
        try:
            features = np.array([[
                self.calculate_bmi(patient_data['height'], patient_data['weight']),
                patient_data['temp'],
                patient_data['systolic_bp'],
                patient_data['diastolic_bp'],
                patient_data['pulse'],
                patient_data['age']
            ]])
            prediction = self.model.predict(features)
            probability = self.model.predict_proba(features).max()
            return {
                'disease': self.label_encoder.inverse_transform(prediction)[0],
                'confidence': round(probability * 100, 2)
            }
        except Exception as e:
            return f"Prediction error: {str(e)}"