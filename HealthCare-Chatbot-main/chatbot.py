import os
from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
import pandas as pd
import csv
import random
import datetime
from collections import defaultdict
import re
import nltk
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords

nltk.download('punkt')
nltk.download('stopwords')

app = Flask(__name__)
CORS(app)

# Load data
#symptoms_conditions_df = pd.read_csv('data/symptoms_conditions1.csv')
symptoms_conditions_df = pd.read_csv('C:/Users/ROHAN/Downloads/HealthCare-Chatbot-main/HealthCare-Chatbot-main/data/symptoms_conditions1.csv')

conditions_treatments_df = pd.read_csv('C:/Users/ROHAN/Downloads/HealthCare-Chatbot-main/HealthCare-Chatbot-main/data/conditions_treatments.csv')

symptoms_conditions_dict = symptoms_conditions_df.groupby('Symptom')['Condition'].apply(list).to_dict()
conditions_treatments_dict = conditions_treatments_df.groupby('Condition')['Treatment'].apply(list).to_dict()

# User state
user_state = defaultdict(lambda: {'name': None, 'conversation_stage': 'get_name', 'condition': None, 'duration': None, 'symptoms': []})

# Load doctors and appointments
def load_csv(filename):
    with open(filename, 'r') as f:
        return list(csv.DictReader(f))

doctors = load_csv('C:/Users/ROHAN/Downloads/HealthCare-Chatbot-main/HealthCare-Chatbot-main/data/doctors.csv')
appointments = load_csv('C:/Users/ROHAN/Downloads/HealthCare-Chatbot-main/HealthCare-Chatbot-main/data/appointments.csv')

def save_appointment(appointment):
    fieldnames = ['ID', 'Name', 'Time', 'Date', 'Illness', 'Doctor', 'Title', 'Description']
    with open('data/appointments.csv', 'a', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        if f.tell() == 0:
            writer.writeheader()
        writer.writerow(appointment)

def get_available_slots(date):
    booked_slots = [apt['Time'] for apt in appointments if apt['Date'] == date]
    all_slots = [f"{h:02d}:00" for h in range(8, 21)]  # Expanded to cover all hours from 8 AM to 8 PM
    return [slot for slot in all_slots if slot not in booked_slots]

def find_closest_slot(preferred_time, available_slots):
    preferred_minutes = int(preferred_time[:2]) * 60 + int(preferred_time[3:])
    closest_slot = min(available_slots, key=lambda x: abs(preferred_minutes - (int(x[:2]) * 60 + int(x[3:]))))
    return closest_slot

def get_greeting(name):
    greetings = [
        f"👋 Hello {name}! How can I assist you today?",
        f"Hi there, {name}! 😊 What brings you here?",
        f"Greetings, {name}! 🌟 How may I help you?",
        f"Welcome, {name}! 🤗 What would you like to know?",
        f"Hey {name}! 👨‍⚕️ How can I be of service today?"
    ]
    return random.choice(greetings)

def is_greeting(message):
    greetings = ['hi', 'hello', 'hey', 'greetings', 'hola']
    return any(greeting in message.lower() for greeting in greetings)

def preprocess_text(text):
    # Tokenize and remove stopwords
    stop_words = set(stopwords.words('english'))
    tokens = word_tokenize(text.lower())
    return [token for token in tokens if token not in stop_words]

def match_symptoms(user_input):
    preprocessed_input = preprocess_text(user_input)
    matched_symptoms = []
    
    for symptom in symptoms_conditions_dict.keys():
        if any(token in preprocess_text(symptom) for token in preprocessed_input):
            matched_symptoms.append(symptom)
    
    return matched_symptoms

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/chatbot', methods=['POST'])
def chatbot():
    try:
        data = request.json
        user_input = data.get('message', '').strip()
        session_id = data.get('session_id', 'default')

        state = user_state[session_id]

        if state['conversation_stage'] == 'get_name':
            if user_input.lower() == 'reset':
                user_state[session_id] = {'name': None, 'conversation_stage': 'get_name', 'condition': None, 'duration': None, 'symptoms': []}
                return jsonify({'response': "Let's start over. What should I call you?"})

            state['name'] = user_input
            state['conversation_stage'] = 'chat'
            return jsonify({'response': get_greeting(user_input)})

        user_name = state['name']

        if is_greeting(user_input):
            return jsonify({'response': get_greeting(user_name)})

        if state['conversation_stage'] == 'ask_duration':
            try:
                duration = int(user_input)
                state['duration'] = duration
                state['conversation_stage'] = 'chat'
                if duration >= 5:
                    return jsonify({'response': f"{user_name}, since you've been experiencing these symptoms for {duration} days, which is 5 or more days, I recommend consulting a doctor. Are you currently at Ganpat University campus? (Yes/No)"})
                else:
                    return jsonify({'response': f"I understand, {user_name}. Since it's been less than 5 days, please monitor your symptoms closely. If they persist or worsen, please consult a doctor. Is there anything else I can help you with?"})
            except ValueError:
                return jsonify({'response': f"I'm sorry, {user_name}, but I didn't understand that. Could you please enter the number of days you've been experiencing these symptoms?"})

        # Symptom matching logic
        matched_symptoms = match_symptoms(user_input)
        state['symptoms'].extend(matched_symptoms)
        
        if matched_symptoms:
            all_conditions = [condition for symptom in state['symptoms'] for condition in symptoms_conditions_dict.get(symptom, [])]
            if all_conditions:
                condition = max(set(all_conditions), key=all_conditions.count)
                state['condition'] = condition
                treatments = conditions_treatments_dict.get(condition, ["Consult a healthcare professional"])
                response = f"{user_name}, based on your symptoms, you may have {condition}. Suggested precautions or treatments include: {', '.join(treatments)}."
                response += f"\n\n{user_name}, how many days have you been experiencing these symptoms?"
                state['conversation_stage'] = 'ask_duration'
            else:
                response = f"I've noted your symptoms, {user_name}. Could you provide more details about how you're feeling?"
        else:
            response = f"I'm not sure about your condition based on the information provided, {user_name}. Could you tell me more about your symptoms?"
        
        return jsonify({'response': response})

    except Exception as e:
        app.logger.error(f"An error occurred: {str(e)}")
        return jsonify({'response': "I apologize, but an error occurred. Please try again or contact support if the problem persists."})

@app.route('/book_appointment', methods=['POST'])
def handle_appointment():
    try:
        data = request.json
        session_id = data.get('session_id', 'default')
        name = user_state[session_id]['name']
        illness = user_state[session_id]['condition']
        preferred_time = data.get('preferred_time')

        if not all([name, illness, preferred_time]):
            return jsonify({'response': "I'm sorry, but I'm missing some information. Could you please provide all the necessary details for booking an appointment?"})

        # Use current date for the appointment
        current_date = datetime.datetime.now()
        appointment_date = current_date.strftime("%Y-%m-%d")

        # Check if the preferred time is in the future
        preferred_datetime = datetime.datetime.strptime(f"{appointment_date} {preferred_time}", "%Y-%m-%d %H:%M")
        if preferred_datetime <= current_date:
            return jsonify({'response': f"I'm sorry {name}, but the requested time has already passed. Please choose a future time for your appointment."})

        available_slots = get_available_slots(appointment_date)
        
        if preferred_time not in available_slots:
            closest_slot = find_closest_slot(preferred_time, available_slots)
            return jsonify({'response': f"I'm sorry {name}, but the slot at {preferred_time} on {appointment_date} is not available. The closest available slot is at {closest_slot}. Would you like to book this slot? (Yes/No)"})

        # Assign a doctor (for simplicity, we're assigning the first doctor)
        assigned_doctor = doctors[0]['Name']

        appointment_id = f"APPT-{random.randint(1000, 9999)}"
        appointment = {
            'ID': appointment_id,
            'Name': name,
            'Time': preferred_time,
            'Date': appointment_date,
            'Illness': illness,
            'Doctor': assigned_doctor,
            'Title': f"Appointment for {illness}",
            'Description': f"Consultation for {illness} symptoms"
        }
        
        save_appointment(appointment)
        
        response = f"Great news, {name}! Your appointment has been booked successfully!\n"
        response += f"Appointment ID: {appointment_id}\n"
        response += f"Doctor: {assigned_doctor}\n"
        response += f"Date: {appointment_date}\n"
        response += f"Time: {preferred_time}\n"
        response += f"Please arrive at the Guni Health Clinic (opposite the shopping center) a few minutes before your appointment time."
        
        return jsonify({'response': response})

    except Exception as e:
        app.logger.error(f"An error occurred while booking the appointment: {str(e)}")
        return jsonify({'response': "I apologize, but an error occurred while booking your appointment. Please try again or contact our support team for assistance."})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)), debug=True)