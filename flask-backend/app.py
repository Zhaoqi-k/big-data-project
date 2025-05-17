from flask import Flask, request, jsonify, render_template
from flask_limiter import Limiter
from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileRequired
from flask_caching import Cache
from flask_cors import CORS

import re
import uuid
from PyPDF2 import PdfReader
from datetime import datetime, date
from supabase import create_client, Client
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

# Create folder in server that stores uploaded files
app.config["ALLOWED_EXTENSIONS"] = {"pdf"}
app.config["UPLOADS_FOLDER"] = "uploads/"
os.makedirs(app.config["UPLOADS_FOLDER"], exist_ok=True)

# Make sure the file is a pdf
def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in app.config["ALLOWED_EXTENSIONS"]

# Read pdf text
def extract_text_from_pdf(pdf):
    with open(pdf, "rb") as file:
        reader = PdfReader(file)
        text = ""
        for page in reader.pages:
            text += page.extract_text()
        return text

def split_by_subject(text):
    pattern = "Course:\s+([A-Z]{2})\s+.*?Teacher:\s+.*?\nComments:\s\n(.*?)(?=Course:|\Z)"
    comments = re.findall(pattern, text, re.DOTALL)
    return comments

CORS(app, resources={r"/*": {"origins": "*"}})  # Allows all origins

CORS(app)

# Configure logging
logging.basicConfig(level=logging.DEBUG)

# Create supabase client
supabase_url = os.getenv("SUPABASE_URL")
supabase_key = os.getenv("SUPABASE_ANON_KEY")
supabase: Client = create_client(supabase_url, supabase_key)

@app.route('/')
def index():
    return render_template('index.html')


@app.route('/api/analyze', methods=['POST'])
def analyze_comments():
    if "file" not in request.files:
        return jsonify({"error": "No file uploaded"}), 400

    file = request.files["file"]
    student_id = request.form.get("student_id")
    graduation_year = int(request.form.get("graduation_year"))
    purge_date = date(graduation_year, 7, 1)
    if not student_id:
        return jsonify({"error": "No student ID provided"}), 400
    namespace = uuid.UUID(os.getenv("my_uuid"))
    encrypted_id = str(uuid.uuid5(namespace, student_id))
    
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config["UPLOADS_FOLDER"], filename)
        file.save(filepath)

        report_card_text = extract_text_from_pdf(filepath)
        subjects = split_by_subject(report_card_text)
        history = supabase.table("student_history")\
            .select("subject", "progression_summary", "focus_rec")\
            .eq("encrypted_id", encrypted_id)\
            .order("subject")\
            .execute()

        # Construct a prompt for Gemini
        prompt = f"""
        Here are a student's midterm comments, structured as a list of ("subject", "comments") tuples:
        {subjects}

        Student History: {history.data if history.data else "No history"}
        
        The possible subject abbreviations are: 
        EN (English), 
        MA (math), 
        SC (science), 
        LA (language), 
        HI (history), 
        IN (interdisciplinary),
        RP (religion and philosophy)
        PA (performing arts),
        VA (visual arts).

        Your job is to:
        1. Infer which course is which subject in the student midterm from the subject abbreviation. If the subject abbreviations do not match, leave the subject blank.
        2. Identify clear patterns or changes in student performance, skills, and behavior.
        3. Return a concise structured JSON with:
        - "subject": the subject from the list given above
        - "progression_summary": 3-5 sentence summary of how the student has changed from previous comments
        - "focus_recommendation": 1-3 skills or behaviors to improve on
        
        """

        try:
            # Call Gemini AI
            response = model.generate_content(prompt)
            response_text = response.text.strip()

            
            # Save student history to supabase
            supabase.table("student_history").insert({
                "encrypted_id": encrypted_id,
                "subject": response_text("subject"),
                "date": datetime.now().isoformat(),
                "progression_summary": response_text("progression_summary"),
                "focus_rec": response_text("focus_recommendation"),
                "purge_after": purge_date.isoformat()
            }).execute()
            
            response_text = response_text.replace("```json", "").replace("```", "").strip()

            logging.debug(f"Cleaned Response from Gemini: {response_text}")

            response_json = json.loads(response)

            logging.debug(f"Response from Gemini: {response_json}")

            # Convert response text to JSON format
            return jsonify(response_json), 200

        except json.JSONDecodeError as e:
            logging.error(f"JSON decoding error: {str(e)}")
            return jsonify({"error": "Invalid JSON format from Gemini"}), 500
        except Exception as e:
            logging.error(f"An error occurred: {str(e)}")
            return jsonify({"error": str(e)}), 500
        finally:
            if os.path.exists(filepath):
                os.remove(filepath)

app.route("/api/feedback", methods=["POST"])
def save_feedback():
    habits = request.form.get("habits")
    for habit, rating in habits.items():
        supabase.table("study_habits").insert({
            "habit": habit,
            "rating": rating,
            "date": datetime.now().isoformat()
        })

def get_feedback():
    response = supabase.table("study_habits") \
        .select("habit", "rating") \
        .order("rating", desc=True) \
        .limit(5) \
        .execute()
    if response.data:
        return "Useful study habits include: ", [habit["habit"] for habit in response.data]
    return "Not suggestions available yet"

if __name__ == '__main__':
    os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)
    app.run(debug=True)