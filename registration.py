import streamlit as st
import mysql.connector
import base64
from datetime import datetime, timedelta
import os
import json

def connect_to_db():
    try:
        conn = mysql.connector.connect(
            host="localhost",
            user="root",
            password="mysql",
            database="healthcare"
        )
        
        cursor = conn.cursor()
        cursor.execute("""
            SELECT COUNT(*)
            FROM information_schema.tables
            WHERE table_schema = 'healthcare' 
            AND table_name = 'patients'
        """)
        
        if cursor.fetchone()[0] == 0:
            cursor.execute("""
                CREATE TABLE patients (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    name VARCHAR(100) NOT NULL,
                    age INT NOT NULL,
                    gender VARCHAR(20) NOT NULL,
                    locality VARCHAR(100) NOT NULL,
                    registration_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            conn.commit()
            st.success("Created patients table in the database")
            
        cursor.close()
        return conn
        
    except mysql.connector.Error as err:
        st.error(f"Database connection error: {err}")
        return None

def insert_patient(name, age, gender, locality):
    conn = connect_to_db()
    if conn is None:
        return False
    
    try:
        cursor = conn.cursor()
        query = "INSERT INTO patients (name, age, gender, locality) VALUES (%s, %s, %s, %s)"
        values = (name, age, gender, locality)
        cursor.execute(query, values)
        conn.commit()
        return True
    except mysql.connector.Error as err:
        st.error(f"Database error: {err}")
        return False
    finally:
        if 'cursor' in locals():
            cursor.close()
        if conn.is_connected():
            conn.close()

def get_base64_of_image(image_path):
    try:
        with open(image_path, "rb") as image_file:
            return base64.b64encode(image_file.read()).decode()
    except Exception as e:
        st.error(f"Error loading image: {e}")
        return ""

def set_background(image_path):
    base64_img = get_base64_of_image(image_path)
    if base64_img:
        bg_image_style = f"""
        <style>
        .stApp {{
            background-image: url("data:image/png;base64,{base64_img}");
            background-size: cover;
            background-position: center;
            background-repeat: no-repeat;
            background-attachment: fixed;
        }}
        </style>
        """
        st.markdown(bg_image_style, unsafe_allow_html=True)

def apply_custom_css():
    custom_css = """
    <style>
    /* Professional color scheme */
    :root {
        --primary-color: #005b96;
        --secondary-color: #0b3d91;
        --accent-color: #5cb85c;
        --light-color: #f8f9fa;
        --dark-color: #343a40;
    }
    
    /* Heading box */
    .heading-box {
        background-color: var(--primary-color);
        padding: 15px;
        border-radius: 8px;
        margin-bottom: 25px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    }
    
    /* Doctor specification box */
    .doctor-box {
        background-color: var(--secondary-color);
        padding: 15px;
        border-radius: 8px;
        margin-bottom: 20px;
        color: white;
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
        transition: transform 0.3s ease;
    }
    
    .doctor-box:hover {
        transform: translateY(-3px);
    }
    
    /* Hospital box */
    .hospital-box {
        background-color: var(--light-color);
        padding: 15px;
        border-radius: 8px;
        margin-bottom: 20px;
        color: var(--dark-color);
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
        border-left: 4px solid var(--accent-color);
    }
    
    .available {
        border-left: 4px solid #5cb85c;
    }
    
    .not-available {
        border-left: 4px solid #d9534f;
    }
    
    /* Text color */
    .stMarkdown, .stTextInput, .stNumberInput, .stSelectbox, .stButton button {
        color: var(--dark-color);
    }
    
    /* Button styling */
    .stButton button {
        background-color: var(--primary-color);
        color: white;
        border-radius: 5px;
        padding: 10px 20px;
        margin: 5px;
        border: none;
        transition: background-color 0.3s ease;
    }
    
    .stButton button:hover {
        background-color: var(--secondary-color);
    }
    
    /* Content box */
    .content-box {
        background-color: rgba(255, 255, 255, 0.9);
        padding: 20px;
        border-radius: 8px;
        margin-bottom: 20px;
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
    }
    
    /* Status badges */
    .badge {
        padding: 5px 10px;
        border-radius: 20px;
        font-size: 0.8em;
        font-weight: bold;
        margin-left: 10px;
    }
    
    .available-badge {
        background-color: #d4edda;
        color: #155724;
    }
    
    .not-available-badge {
        background-color: #f8d7da;
        color: #721c24;
    }
    
    /* Chatbot styles */
    .chatbot-container {
        position: fixed;
        bottom: 20px;
        right: 20px;
        width: 350px;
        height: 500px;
        background-color: white;
        border-radius: 10px;
        box-shadow: 0 5px 15px rgba(0,0,0,0.2);
        z-index: 1000;
        display: flex;
        flex-direction: column;
        border: 1px solid #ddd;
    }
    
    .chatbot-header {
        background-color: var(--primary-color);
        color: white;
        padding: 15px;
        border-top-left-radius: 10px;
        border-top-right-radius: 10px;
        font-weight: bold;
        display: flex;
        justify-content: space-between;
        align-items: center;
    }
    
    .chatbot-messages {
        flex-grow: 1;
        padding: 15px;
        overflow-y: auto;
    }
    
    .chatbot-input {
        padding: 15px;
        border-top: 1px solid #ddd;
        display: flex;
    }
    
    .chatbot-input input {
        flex-grow: 1;
        padding: 10px;
        border: 1px solid #ddd;
        border-radius: 20px;
        margin-right: 10px;
    }
    
    .chatbot-input button {
        background-color: var(--primary-color);
        color: white;
        border: none;
        border-radius: 20px;
        padding: 10px 15px;
        cursor: pointer;
    }
    
    .chatbot-toggle {
        position: fixed;
        bottom: 20px;
        right: 20px;
        background-color: var(--primary-color);
        color: white;
        width: 60px;
        height: 60px;
        border-radius: 50%;
        display: flex;
        justify-content: center;
        align-items: center;
        box-shadow: 0 2px 10px rgba(0,0,0,0.2);
        cursor: pointer;
        z-index: 1001;
    }
    
    /* Responsive design */
    @media (max-width: 768px) {
        .chatbot-container {
            width: 100%;
            height: 70vh;
            bottom: 0;
            right: 0;
            border-radius: 10px 10px 0 0;
        }
    }
    
    /* Chat message styles */
    .user-message {
        background-color: #e3f2fd;
        padding: 10px 15px;
        border-radius: 18px;
        margin-bottom: 10px;
        max-width: 80%;
        align-self: flex-end;
    }
    
    .bot-message {
        background-color: #f1f1f1;
        padding: 10px 15px;
        border-radius: 18px;
        margin-bottom: 10px;
        max-width: 80%;
        align-self: flex-start;
    }
    
    .message-container {
        display: flex;
        flex-direction: column;
        padding: 5px;
    }
    </style>
    """
    st.markdown(custom_css, unsafe_allow_html=True)

# Chatbot functionality
def initialize_chatbot():
    if 'chat_history' not in st.session_state:
        st.session_state['chat_history'] = []
    
    if 'chat_open' not in st.session_state:
        st.session_state['chat_open'] = False

def get_chatbot_response(user_input):
    user_input = user_input.lower()
    
    greetings = ["hi", "hello", "hey", "good morning", "good afternoon"]
    farewells = ["bye", "goodbye", "see you", "thanks"]
    medicine_queries = ["cough", "cold", "fever", "headache", "pain"]
    
    if any(word in user_input for word in greetings):
        return "Hello! I'm your healthcare assistant. How can I help you today?"
    
    if any(word in user_input for word in farewells):
        return "Goodbye! Feel free to reach out if you have any more questions."
    
    if "medicine" in user_input and any(word in user_input for word in medicine_queries):
        if "cough" in user_input:
            return """For cough, you can try these home remedies:
            - Honey and warm water
            - Ginger tea
            - Steam inhalation
            - Saltwater gargle
            
            If symptoms persist for more than 3 days, please consult a doctor."""
        
        if "cold" in user_input:
            return """For cold symptoms:
            - Stay hydrated
            - Get plenty of rest
            - Use a humidifier
            - Try chicken soup
            
            Over-the-counter cold medicines may help, but consult a pharmacist first."""
        
        if "fever" in user_input:
            return """For fever management:
            - Stay hydrated
            - Rest
            - Take paracetamol as directed
            - Use cool compresses
            
            If fever is above 102°F (39°C) or lasts more than 3 days, seek medical attention."""
    
    if "appointment" in user_input:
        return "You can schedule an appointment with our doctors through the 'Our Expert Doctors' page. Would you like me to take you there?"
    
    if "hospital" in user_input or "availability" in user_input:
        return "You can check hospital availability on the 'Hospital Availability' page. Would you like me to direct you there?"
    
    return "I'm sorry, I didn't understand your question. I can help with information about medicines, appointments, and hospital availability. Please try asking in a different way."

def display_chatbot_ui():
    if st.session_state['chat_open']:
        st.markdown("""
        <div class="chatbot-container">
            <div class="chatbot-header">
                <span>Healthcare Assistant</span>
                <button onclick="window.parent.document.dispatchEvent(new CustomEvent('toggle-chatbot'))" 
                        style="background: none; border: none; color: white; cursor: pointer; font-size: 20px;">×</button>
            </div>
            <div class="chatbot-messages" id="chat-messages">
        """, unsafe_allow_html=True)
        
        # Display chat messages
        for chat in st.session_state['chat_history']:
            if chat['is_user']:
                st.markdown(f"""
                <div class="message-container">
                    <div class="user-message">{chat['message']}</div>
                </div>
                """, unsafe_allow_html=True)
            else:
                st.markdown(f"""
                <div class="message-container">
                    <div class="bot-message">{chat['message']}</div>
                </div>
                """, unsafe_allow_html=True)
        
        st.markdown("</div>", unsafe_allow_html=True)
        
        # Chat input
        user_input = st.text_input("Type your message...", key="chat_input", 
                                 on_change=process_chat_input, 
                                 label_visibility="collapsed")
        
        st.markdown("""
            <script>
            // Scroll to bottom of chat
            window.parent.document.getElementById('chat-messages').scrollTop = 
                window.parent.document.getElementById('chat-messages').scrollHeight;
            </script>
        """, unsafe_allow_html=True)
        
        st.markdown("</div>", unsafe_allow_html=True)
    
    # Chat toggle button
    st.markdown(f"""
    <div class="chatbot-toggle" onclick="window.parent.document.dispatchEvent(new CustomEvent('toggle-chatbot'))">
        <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
            <path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"></path>
        </svg>
    </div>
    """, unsafe_allow_html=True)
    
    # JavaScript to handle toggle
    st.markdown("""
    <script>
    document.addEventListener('toggle-chatbot', function() {
        // This event will be caught by Streamlit and handled in Python
        window.parent.document.querySelector('iframe').contentWindow.postMessage('toggle-chatbot', '*');
    });
    </script>
    """, unsafe_allow_html=True)

def process_chat_input():
    if st.session_state.chat_input:
        user_input = st.session_state.chat_input
        st.session_state['chat_history'].append({'message': user_input, 'is_user': True})
        
        bot_response = get_chatbot_response(user_input)
        st.session_state['chat_history'].append({'message': bot_response, 'is_user': False})
        
        # Clear the input
        st.session_state.chat_input = ""

def display_doctor_page():
    st.set_page_config(page_title="Doctor Information", page_icon="👨‍⚕️", layout="centered")
    set_background(r"C:\Users\itsga\Downloads\mainwall2.jpg")
    apply_custom_css()
    initialize_chatbot()

    st.markdown("""
    <div class="heading-box">
        <h1 style="color: white; text-align: center;">Our Expert Doctors</h1>
        <p style="color: white; text-align: center;">Meet our team of experienced healthcare professionals</p>
    </div>
    """, unsafe_allow_html=True)

    doctors = [
        {"name": "Dr. AK Verma", "specialty": "Cardiologist", "image": r"C:\Users\itsga\Downloads\04431a327584e47601fe1c895bd46a24.jpg", "description": "Specialist in heart-related issues with 10+ years of experience."},
        {"name": "Dr. Kabir Singh", "specialty": "Dermatologist", "image": r"C:\Users\itsga\Downloads\d3.jpg", "description": "Expert in skin care and treatments with 8+ years of experience."},
        {"name": "Dr. Ashi", "specialty": "Surgeon", "image": r"C:\Users\itsga\Downloads\d2.jpg", "description": "Specialist in surgical procedures with 8+ years of experience."}
    ]

    for doctor in doctors:
        col1, col2 = st.columns([1, 3])
        with col1:
            try:
                st.image(doctor["image"], width=150)
            except:
                st.warning(f"Could not load image for {doctor['name']}")
        with col2:
            st.markdown(
                f"""
                <div class="doctor-box">
                    <h3 style="color: white;">{doctor['name']}</h3>
                    <p><strong>Specialty:</strong> {doctor['specialty']}</p>
                    <p><strong>About:</strong> {doctor['description']}</p>
                </div>
                """,
                unsafe_allow_html=True
            )
            if st.button(f"Schedule with {doctor['name']}"):
                st.session_state['selected_doctor'] = doctor['name']
                st.session_state['page'] = 'appointment'
                st.rerun()

    st.markdown("---")
    col1, col2 = st.columns(2)
    with col1:
        if st.button("Back to Registration"):
            st.session_state['page'] = 'registration'
            st.rerun()
    with col2:
        if st.button("Check Hospital Availability"):
            st.session_state['page'] = 'availability'
            st.rerun()
    
    display_chatbot_ui()

def display_appointment_page():
    st.set_page_config(page_title="Doctor Appointment", page_icon="📅", layout="centered")
    set_background(r"C:\Users\itsga\Downloads\mainwall2.jpg")
    apply_custom_css()
    initialize_chatbot()

    st.markdown("""
    <div class="heading-box">
        <h1 style="color: white; text-align: center;">Doctor Appointment Scheduling</h1>
        <p style="color: white; text-align: center;">Please select a date and time to schedule your appointment.</p>
    </div>
    """, unsafe_allow_html=True)

    st.subheader("Select a Date")
    today = datetime.today()
    dates = [today + timedelta(days=i) for i in range(7)]
    selected_date = st.selectbox("Choose a date", dates, format_func=lambda x: x.strftime('%Y-%m-%d'))

    if 'selected_doctor' in st.session_state:
        st.markdown(
            f"""
            <div class="content-box">
                <h3>Appointment with {st.session_state['selected_doctor']}</h3>
            </div>
            """,
            unsafe_allow_html=True
        )

    time_slots = ["09:00 AM", "11:00 AM", "01:00 PM", "03:00 PM", "05:00 PM"]
    selected_time = st.selectbox("Choose a time slot", time_slots)
    
    if st.button("Confirm Appointment"):
        st.success(f"Appointment scheduled with {st.session_state['selected_doctor']} on {selected_date.strftime('%Y-%m-%d')} at {selected_time}.")
        st.session_state['selected_date'] = selected_date
        st.session_state['selected_time'] = selected_time

    st.markdown("---")
    col1, col2 = st.columns(2)
    with col1:
        if st.button("Back to Doctors"):
            st.session_state['page'] = 'doctor'
            st.rerun()
    with col2:
        if st.button("Check Hospital Availability"):
            st.session_state['page'] = 'availability'
            st.rerun()
    
    display_chatbot_ui()

def display_availability_page():
    st.set_page_config(page_title="Hospital Availability", page_icon="🏥", layout="centered")
    set_background(r"C:\Users\itsga\Downloads\back3rd.jpg")
    apply_custom_css()
    initialize_chatbot()

    st.markdown("""
    <div class="heading-box">
        <h1 style="color: white; text-align: center;">Hospital Availability</h1>
        <p style="color: white; text-align: center;">Check hospital availability and nearby options</p>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("""
    <div class="content-box">
        <h3>Hospital Availability Status</h3>
        <p>Real-time availability of our network hospitals</p>
    </div>
    """, unsafe_allow_html=True)
    
    if 'selected_date' in st.session_state and 'selected_time' in st.session_state:
        st.write(f"Checking availability for {st.session_state['selected_date'].strftime('%Y-%m-%d')} at {st.session_state['selected_time']}...")
    else:
        st.write("No appointment scheduled yet. Please schedule an appointment first.")
    
    hospitals = [
        {
            "name": "VERMA Hospital", 
            "available": True,
            "image": r"C:\Users\itsga\Downloads\doctor1.jpg",
            "address": "Jankpuri West",
            "phone": "7701815002",
            "beds": 25,
            "specialties": ["Cardiology", "General Medicine", "Pediatrics"]
        },
        {
            "name": "Mata Rukmani Devi Hospital", 
            "available": False,
            "image": r"C:\Users\itsga\Downloads\hospital3.jpg",
            "address": "Dwarka Mor",
            "phone": "8708464668",
            "beds": 50,
            "specialties": ["Orthopedics", "Neurology", "Oncology"]
        },
        {
            "name": "Yadav Clinic", 
            "available": True,
            "image": r"C:\Users\itsga\Downloads\hospital 2.jpg",
            "address": "Uttam Nagar",
            "phone": "7668451843",
            "beds": 15,
            "specialties": ["General Practice", "Dermatology", "ENT"]
        }
    ]
    
    for hospital in hospitals:
        col1, col2 = st.columns([1, 3])
        with col1:
            try:
                st.image(hospital["image"], width=150)
            except:
                st.warning(f"Could not load image for {hospital['name']}")
        with col2:
            status = "Available" if hospital["available"] else "Not Available"
            badge_class = "available-badge" if hospital["available"] else "not-available-badge"
            
            st.markdown(
                f"""
                <div class="hospital-box {'available' if hospital['available'] else 'not-available'}">
                    <h3>{hospital['name']} <span class="badge {badge_class}">{status}</span></h3>
                    <p><strong>Address:</strong> {hospital['address']}</p>
                    <p><strong>Phone:</strong> {hospital['phone']}</p>
                    <p><strong>Available Beds:</strong> {hospital['beds'] if hospital['available'] else '0'}</p>
                    <p><strong>Specialties:</strong> {', '.join(hospital['specialties'])}</p>
                    <div style="margin-top: 10px;">
                """,
                unsafe_allow_html=True
            )
            
            col1, col2 = st.columns(2)
            with col1:
                if st.button(f"View Details - {hospital['name']}"):
                    st.session_state['selected_hospital'] = hospital['name']
                    st.session_state['page'] = 'hospital_details'
                    st.rerun()
            with col2:
                if st.button(f"Get Directions - {hospital['name']}"):
                    st.write(f"Opening directions to {hospital['name']} in your map application...")
    
    st.markdown("---")
    col1, col2 = st.columns(2)
    with col1:
        if st.button("Back to Doctors"):
            st.session_state['page'] = 'doctor'
            st.rerun()
    with col2:
        if st.button("Back to Registration"):
            st.session_state['page'] = 'registration'
            st.rerun()
    
    display_chatbot_ui()

def display_registration_page():
    st.set_page_config(page_title="Patient Registration", page_icon="🏥", layout="centered")
    set_background(r"C:\Users\itsga\Downloads\mainwall1.jpg")
    apply_custom_css()
    initialize_chatbot()

    st.markdown("""
    <div class="heading-box">
        <h1 style="color: white; text-align: center;">Patient Registration Form</h1>
        <p style="color: white; text-align: center;">Please fill out the form below to register.</p>
    </div>
    """, unsafe_allow_html=True)

    name = st.text_input("Full Name", placeholder="Enter your full name")
    age = st.number_input("Age", min_value=0, max_value=120, step=1, placeholder="Enter your age")
    gender = st.selectbox("Gender", ["Male", "Female", "Other"])
    locality = st.text_input("Locality", placeholder="Enter your locality")

    if st.button("Register"):
        if name and age and gender and locality:
            if insert_patient(name, age, gender, locality):
                st.success("Registration successful! Thank you for registering.")
                st.session_state['page'] = 'doctor'
                st.rerun()
            else:
                st.error("Registration failed. Please try again.")
        else:
            st.error("Please fill out all fields.")
    
    display_chatbot_ui()

def main():
    if 'page' not in st.session_state:
        st.session_state['page'] = 'registration'

    # Handle chatbot toggle from JavaScript
    if st.session_state.get('toggle_chatbot'):
        st.session_state['chat_open'] = not st.session_state.get('chat_open', False)
        st.session_state.pop('toggle_chatbot')

    if st.session_state['page'] == 'registration':
        display_registration_page()
    elif st.session_state['page'] == 'doctor':
        display_doctor_page()
    elif st.session_state['page'] == 'appointment':
        display_appointment_page()
    elif st.session_state['page'] == 'availability':
        display_availability_page()

if __name__ == "__main__":
    main()