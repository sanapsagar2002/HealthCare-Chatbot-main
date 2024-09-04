# HealthCare Chatbot

## Description
HealthCare Chatbot is an AI-powered assistant designed to provide initial medical guidance and appointment scheduling. It uses natural language processing to understand user symptoms, suggest potential conditions, and offer basic health advice. The chatbot can also book appointments with healthcare professionals at the Guni Health Clinic.

## Features
- Symptom analysis and condition suggestion
- Basic health advice and precautions
- Appointment scheduling with real-time availability checking
- User-friendly web interface

## Technologies Used
- Python 3.8+
- Flask (Web Framework)
- NLTK (Natural Language Processing)
- Pandas (Data Manipulation)
- HTML/CSS/JavaScript (Frontend)
- jQuery (AJAX requests)

## Installation

1. Clone the repository:
```bash
git clone https://github.com/AdesharaBrijesh/HealthCare-Chatbot.git
cd HealthCare-Chatbot
```

2. Set up a virtual environment:
```bash
python -m venv chatbot_env
source chatbot_env/bin/activate  # On macOS and Linux
chatbot_env\Scripts\activate  # On Windows
```

3. Install the required packages:
```bash
pip install -r requirements.txt
```

5. Download NLTK data:
```bash
python -m nltk.downloader punkt stopwords
```

## Usage

1. Start the Flask server:
```bash
python chatbot.py
```
2. Open a web browser and navigate to `http://localhost:5000`

3. Interact with the chatbot by typing your symptoms or health concerns

## Project Structure
- `chatbot.py`: Main application file
- `templates/index.html`: HTML template for the web interface
- `static/styles.css`: CSS styles for the web interface
- `data/`: Directory containing CSV files with medical data
- `symptoms_conditions1.csv`: Mapping of symptoms to conditions
- `conditions_treatments.csv`: Treatments for various conditions
- `doctors.csv`: List of available doctors
- `appointments.csv`: Record of booked appointments

## Contributing
Contributions to improve HealthCare Chatbot are welcome. Please follow these steps:

1. Fork the repository
2. Create a new branch 
```bash
git checkout -b feature/AmazingFeature
```
4. Commit your changes 
```bash
git commit -m 'Add some AmazingFeature'
```
5. Push to the branch 
```bash
git push origin feature/AmazingFeature
```
6. Open a Pull Request

## License
This project is open source and available under the [MIT License](LICENSE).

## Contact
Brijesh Adeshara - adesharabrijesh8@gmail.com

Dharmik Thakkar - thakkardharmik437@gmail.com

Vishwas Chaudhary - vishwaschaudhary21@gnu.ac.in

Project Link: [https://github.com/AdesharaBrijesh/HealthCare-Chatbot](https://github.com/AdesharaBrijesh/HealthCare-Chatbot)

## Acknowledgements
- [Flask](https://flask.palletsprojects.com/)
- [NLTK](https://www.nltk.org/)
- [Pandas](https://pandas.pydata.org/)
- [jQuery](https://jquery.com/)
