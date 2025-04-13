from flask import Flask, request, jsonify, render_template
from flask_limiter import Limiter
from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileRequired
from flask_caching import Cache
from flask_cors import CORS

from PyPDF2 import PdfReader
from datetime import datetime
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


@app.route('/analyze', methods=['POST'])
def analyze_comments():
    if "file" not in request.files:
        return jsonify({"error": "No file uploaded"}), 400

    file = request.files["file"]
    student_id = request.form.get("student_id")
    grad_date = datetime(request.form.get("graduation_date"))
    if not student_id:
        return jsonify({"error": "No student ID provided"}), 400
    habits = request.form.get("habits")
    
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config["UPLOADS_FOLDER"], filename)
        file.save(filepath)

        report_card_text = extract_text_from_pdf(filepath)
        history = supabase.table("student_history").select("*").eq("student_id", student_id).execute()

        # Construct a prompt for Gemini
        prompt = f"""
        Analyze the following student report card feedback:
        {report_card_text}

        Student History: {history.data if history.data else "No history"}

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
            supabase.table("student_history").insert({
                "student_id": student_id,
                "date": datetime.now().isoformat(),
                "analysis": response.text.strip(),
                "purge_after": grad_date
            }).execute()

            logging.debug(f"Cleaned Response from Gemini: {response}")

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

app.route("/feedback", methods=["POST"])
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