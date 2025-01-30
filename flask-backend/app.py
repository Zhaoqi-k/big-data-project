from flask import Flask, request, jsonify
import json
from flask_cors import CORS
import google.generativeai as genai
import os
import logging
from dotenv import load_dotenv

# Load the environment variables + API key
load_dotenv()
GEMINI_API_KEY = os.getenv("my_api_key")
genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel(model_name="gemini-1.5-flash")



#Create a Flask app
app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})  # Allows all origins

CORS(app)

# Configure logging
logging.basicConfig(level=logging.DEBUG)

@app.route('/analyze', methods=['POST'])
def analyze():
    data = request.json
    report_card_text = data.get('text', '')

    if not report_card_text:
        return jsonify({"error": "No report card text provided"}), 400

    # Construct a prompt for Gemini
    prompt = f"""
    Analyze the following student report card feedback:
    {report_card_text}

    Provide a **concise 75-word student feedback report** with:
    - **2 strengths of student**
    - **2 areas to improve**

    Format the response as JSON:
    {{
      "strengths": ["", ""],
      "areas_to_improve": ["", ""]
    }}
    """

    try:
        # Call Gemini AI
        response = model.generate_content(prompt)
        response_text = response.text.strip()

        response_text = response_text.replace("```json", "").replace("```", "").strip()

        logging.debug(f"Cleaned Response from Gemini: {response_text}")

        response_json = json.loads(response_text)


        logging.debug(f"Response from Gemini: {response_text}")

        # Convert response text to JSON format
        return jsonify(response_json), 200

    except json.JSONDecodeError as e:
        logging.error(f"JSON decoding error: {str(e)}")
        return jsonify({"error": "Invalid JSON format from Gemini"}), 500
    except Exception as e:
        logging.error(f"An error occurred: {str(e)}")
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)