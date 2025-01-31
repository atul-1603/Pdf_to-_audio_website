from flask import Flask, render_template, request, redirect, url_for, send_from_directory, flash, jsonify
from werkzeug.utils import secure_filename
from gtts import gTTS
import pyttsx3  # For local voice synthesis
from googletrans import Translator
import os
import logging
from pymongo import MongoClient
from PyPDF2 import PdfReader
from datetime import datetime
from gridfs import GridFS  # Import GridFS for file storage
from bson import ObjectId  # To handle MongoDB ObjectIds
from flask import Response

# Configure logging
logging.basicConfig(level=logging.DEBUG)

# Initialize Flask app
app = Flask(__name__)
app.secret_key = 'supersecretkey'

# MongoDB Atlas Connection
MONGO_URI = "mongodb+srv://Atul1603:Atuldubey@pdftoaudio.8pkov.mongodb.net/UserDataBase?retryWrites=true&w=majority&appName=PdfToAudio"
client = MongoClient(MONGO_URI)
db = client['UserDataBase']
history_collection = db['history']
fs = GridFS(db)  # Initialize GridFS

# Directory paths
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
UPLOAD_FOLDER = os.path.join(BASE_DIR, 'uploads')
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/convert', methods=['POST'])
def convert():
    try:
        pdf_file = request.files.get('file')
        language = request.form.get('language')
        voice_type = request.form.get('voice')

        if not pdf_file or not language or not voice_type:
            flash("All fields are required!", "error")
            return redirect(url_for('index'))

        filename = secure_filename(pdf_file.filename)
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        pdf_file.save(file_path)
        logging.debug(f"PDF saved at: {file_path}")

        # Extract text from PDF
        reader = PdfReader(file_path)
        text = ''.join([page.extract_text() for page in reader.pages if page.extract_text()])
        
        if not text.strip():
            flash("The uploaded PDF does not contain readable text.", "error")
            return redirect(url_for('index'))
        
        logging.debug(f"Extracted text: {text[:100]}...")

        # Translate text
        translator = Translator()
        translated_text = translator.translate(text, dest=language).text
        logging.debug(f"Translated text: {translated_text[:100]}...")

        # Generate audio
        audio_filename = f"{os.path.splitext(filename)[0]}_{language}_{voice_type}.mp3"
        audio_path = os.path.join(app.config['UPLOAD_FOLDER'], audio_filename)

        if voice_type == "male":
            engine = pyttsx3.init()
            voices = engine.getProperty('voices')
            engine.setProperty('voice', voices[0].id)  # Select male voice
            engine.save_to_file(translated_text, audio_path)
            engine.runAndWait()
        else:
            tts = gTTS(translated_text, lang=language)
            tts.save(audio_path)

        logging.debug(f"Audio file saved at: {audio_path}")

        # Store PDF and audio in MongoDB GridFS
        with open(file_path, "rb") as pdf_data:
            pdf_id = fs.put(pdf_data, filename=filename)

        with open(audio_path, "rb") as audio_data:
            audio_id = fs.put(audio_data, filename=audio_filename)

        # Store metadata in history collection
        history_collection.insert_one({
            'pdf_filename': filename,
            'pdf_id': pdf_id,
            'audio_filename': audio_filename,
            'audio_id': audio_id,
            'language': language,
            'voice': voice_type,
            'upload_date': datetime.utcnow()
        })

        return redirect(url_for('result', audio_filename=audio_filename))

    except Exception as e:
        logging.error(f"Error during processing: {e}")
        flash(f"An error occurred: {str(e)}", "error")
        return redirect(url_for('index'))

@app.route('/result')
def result():
    audio_filename = request.args.get('audio_filename')
    if not audio_filename:
        return "No audio file provided."
    
    audio_url = url_for('serve_audio', filename=audio_filename)
    logging.debug(f"Audio URL for result page: {audio_url}")

    # Fetch history from MongoDB
    history_data = list(history_collection.find({}, {'_id': 0}))

    return render_template('result.html', audio_url=audio_url, history=history_data)

@app.route('/uploads/<filename>')
def serve_audio(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

@app.route('/history_page')
def history_page():
    history_data = list(history_collection.find({}, {'_id': 0}))
    return render_template('history.html', history=history_data)

@app.route('/api/history', methods=['GET'])
def get_history():
    try:
        history_data = list(history_collection.find({}, {'_id': 0}))
        
        if not history_data:
            return jsonify({"error": "No history found"}), 404

        for file in history_data:
            file['pdf_url'] = url_for('download_file', file_id=str(file['pdf_id']))
            file['audio_url'] = url_for('download_file', file_id=str(file['audio_id']))
            file['pdf_id'] = str(file['pdf_id'])  # Convert ObjectId to string
            file['audio_id'] = str(file['audio_id'])  # Convert ObjectId to string

        return jsonify({
            "status": "success",
            "total_files": len(history_data),
            "data": history_data
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/download/<file_id>')
def download_file(file_id):
    try:
        file_data = fs.get(ObjectId(file_id))  # Retrieve file from GridFS
        return Response(file_data.read(), mimetype='application/octet-stream',
                        headers={"Content-Disposition": f"attachment; filename={file_data.filename}"})
    except Exception as e:
        logging.error(f"Error retrieving file with ID {file_id}: {e}")
        return jsonify({"error": "File not found"}), 404
    
if __name__ == '__main__':
    app.run(debug=True)
