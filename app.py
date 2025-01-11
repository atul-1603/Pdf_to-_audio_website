from flask import Flask, render_template, request, redirect, url_for, send_from_directory, flash
from werkzeug.utils import secure_filename
from gtts import gTTS
from googletrans import Translator
import os
import logging

# Configure logging
logging.basicConfig(level=logging.DEBUG)

# Initialize Flask app
app = Flask(__name__)
app.secret_key = 'supersecretkey'  # Required for flashing messages

# Directory paths
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
UPLOAD_FOLDER = os.path.join(BASE_DIR, 'uploads')
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# History log
history = []

# Home Route (Index Page)
@app.route('/')
def index():
    return render_template('index.html')

# Conversion Route
@app.route('/convert', methods=['POST'])
def convert():
    try:
        # Get the uploaded PDF file and selected language
        pdf_file = request.files.get('file')
        language = request.form.get('language')

        # Validate inputs
        if not pdf_file:
            flash("No file uploaded. Please upload a PDF file.", "error")
            return redirect(url_for('index'))
        if not language:
            flash("No language selected. Please choose a language.", "error")
            return redirect(url_for('index'))

        # Save the uploaded file
        filename = secure_filename(pdf_file.filename)
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        pdf_file.save(file_path)
        logging.debug(f"PDF saved at: {file_path}")

        # Extract text from PDF
        from PyPDF2 import PdfReader
        reader = PdfReader(file_path)
        text = ''.join([page.extract_text() for page in reader.pages])
        logging.debug(f"Extracted text: {text[:100]}...")  # Show first 100 characters for debugging

        if not text.strip():
            flash("The uploaded PDF does not contain readable text.", "error")
            return redirect(url_for('index'))

        # Translate text
        translator = Translator()
        translated_text = translator.translate(text, dest=language).text
        logging.debug(f"Translated text: {translated_text[:100]}...")  # Show first 100 characters

        # Convert translated text to audio
        audio_filename = f"{os.path.splitext(filename)[0]}_{language}.mp3"
        audio_path = os.path.join(app.config['UPLOAD_FOLDER'], audio_filename)
        tts = gTTS(translated_text, lang=language)
        tts.save(audio_path)
        logging.debug(f"Audio file saved at: {audio_path}")

        # Add to history
        history.append({'pdf': filename, 'audio': audio_filename})

        # Redirect to result page with audio filename
        return redirect(url_for('result', audio_filename=audio_filename))

    except Exception as e:
        logging.error(f"Error during processing: {e}")
        flash(f"An error occurred: {str(e)}", "error")
        return redirect(url_for('index'))

# Result Page
@app.route('/result')
def result():
    audio_filename = request.args.get('audio_filename')
    if not audio_filename:
        return "No audio file provided."
    audio_url = url_for('serve_audio', filename=audio_filename)
    logging.debug(f"Audio URL for result page: {audio_url}")
    return render_template('result.html', audio_url=audio_url, history=history)

# Serve Audio File
@app.route('/uploads/<filename>')
def serve_audio(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

# Run the Flask app
if __name__ == '__main__':
    app.run(debug=True)
