from flask import Flask, request, jsonify
import os
from flask_cors import CORS
import google.generativeai as genai
from dotenv import load_dotenv
import logging

load_dotenv()
app = Flask(__name__)
CORS(app)

# Configure Google Generative AI with your API key:
genai.configure(api_key=os.getenv("api_key"))

# Instantiate the Gemini model
model = genai.GenerativeModel(model_name="gemini-1.5-flash")

# Configure logging
logging.basicConfig(level=logging.DEBUG)

@app.route('/analyze', methods=['POST'])
def analyze():
    data = request.json
    texts = data.get('texts', [])
    
    # Combine all user text inputs into one string
    combined_text = "\n\n".join(texts)
    
    # Construct a prompt
    prompt = f"""
Analyze the following student feedback report:
{combined_text}

Please provide exactly 3 areas of growth needed, 3 strengths, and 3 specific skills to work on.
Answer in the following JSON format **exactly**:

{{
  "strengths": ["", "", ""],
  "areas_of_growth": ["", "", ""],
  "specific_skills": ["", "", ""]
}}
"""
    try:
        # Send the prompt to the model and get the response
        response = model.generate_content(prompt)
        response_text = response.text.strip('```').strip()  # Remove the backticks and any leading/trailing whitespace
        
        # Log the response text
        logging.debug(f"Response from model: {response_text}")
        print(response_text)
        # Return the response text as plain text
        return response_text, 200, {'Content-Type': 'text/plain'}
    except Exception as e:
        # Handle other errors
        logging.error(f"An error occurred: {str(e)}")
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)
