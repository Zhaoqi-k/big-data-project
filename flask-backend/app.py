from flask import Flask, request, jsonify, render_template
from flask_limiter import Limiter
from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileRequired
from flask_caching import Cache
from flask_cors import CORS

from PyPDF2 import PdfReader
from supabase import create_client, Client
from datetime import datetime
from werkzeug.utils import secure_filename
import json
import google.generativeai as genai
import os
import logging
from dotenv import load_dotenv

# Load the environment variables + API key
load_dotenv()
GEMINI_API_KEY = os.getenv("my_api_key")
genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel(model_name="gemini-1.5-flash")

# Create a Flask app
app = Flask(__name__)
app.config["SECRET_KEY"] = os.getenv("MY_SECRET_KEY")
app.config["ALLOWED_EXTENSIONS"] = {"pdf"}
# Create folder in server that stores uploaded files
app.config["UPLOADS_FOLDER"] = "uploads/"
os.makedirs(app.config["UPLOADS_FOLDER"], exist_ok=True)

def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in app.config["ALLOWED_EXTENSIONS"]

def extract_text_from_pdf(pdf):
    text = pdf.PdfReader

CORS(app, resources={r"/*": {"origins": "*"}})  # Allows all origins

CORS(app)

# Configure logging
logging.basicConfig(level=logging.DEBUG)

# Create supabase client

@app.route('/')
def index():
    return render_template('index.html')


@app.route('/analyze', methods=['POST'])
def analyze_comments():
    data = request.json
    report_card_text = data.get("text", "")

    # If file and allowed_file -> save file to uploads
    # Get student id
    # Extract pdf data
    # Get student history

    if not report_card_text:
        return jsonify({"error": "No report card text provided"}), 400

    # Construct a prompt for Gemini
    prompt = f"""
    Analyze the following student report card feedback:
    {report_card_text}

    Student History: {history.data}

    Provide a **concise 75-word student feedback report** with:
    - **2 strengths of student**
    - **2 areas to improve**
    - **how they have improved based on their previous comments**
    
    """

    try:
        # Call Gemini AI
        response = model.generate_content(prompt)
        #response_text = response.text.strip()

        #response_text = response_text.replace("```json", "").replace("```", "").strip()
        
        # Save student history to supabase

        logging.debug(f"Cleaned Response from Gemini: {response}")

        response_json = json.loads(response)


        logging.debug(f"Response from Gemini: {response_text}")

        # Convert response text to JSON format
        return jsonify(response_json), 200

    except json.JSONDecodeError as e:
        logging.error(f"JSON decoding error: {str(e)}")
        return jsonify({"error": "Invalid JSON format from Gemini"}), 500
    except Exception as e:
        logging.error(f"An error occurred: {str(e)}")
        return jsonify({"error": str(e)}), 500

# app.route
# def get_feedback():

# app.route
# def save_feedback():


if __name__ == '__main__':
    app.run(debug=True)