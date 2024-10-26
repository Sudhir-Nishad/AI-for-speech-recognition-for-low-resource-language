from flask import Flask, render_template, request, jsonify
import os
from werkzeug.utils import secure_filename
from main import MultiLanguageTranslator  # Adjust import based on your structure

app = Flask(__name__)
translator = MultiLanguageTranslator()

# Define folder to store uploads
UPLOAD_FOLDER = 'uploads'
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return "No file part"
    file = request.files['file']
    if file.filename == '':
        return "No selected file"
    if file:
        filename = secure_filename(file.filename)
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(file_path)

        # Process the uploaded audio file using your translator
        original_text = translator.speech_to_text(file_path)
        detected_lang = translator.detect_language(original_text)
        translated_text = translator.translate_text(original_text, 'en')
        translator.text_to_speech(translated_text)  # Convert to speech and save as 'output_audio.mp3'

        # Return the results to the frontend
        result = {
            "original_text": original_text,
            "detected_lang": detected_lang,
            "translated_text": translated_text,
            "audio_file": "output_audio.mp3"  # Make sure this file is accessible
        }
        return jsonify(result)

if __name__ == '__main__':
    app.run(debug=True)
