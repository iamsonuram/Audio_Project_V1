from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from flask_sqlalchemy import SQLAlchemy
from werkzeug.utils import secure_filename
import os
from deep_translator import GoogleTranslator
from indic_transliteration.sanscript import transliterate, ITRANS
import requests
import speech_recognition as sr
from pydub import AudioSegment

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['SECRET_KEY'] = 'audio_project'
app.config['UPLOAD_FOLDER'] = 'static/uploads/'
app.config['ALLOWED_EXTENSIONS'] = {'jpg', 'png', 'jpeg', 'webm'}

db = SQLAlchemy(app)

# Ensure upload folder exists
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# Database Model
class Submission(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    word = db.Column(db.String(100), nullable=False)
    transit = db.Column(db.String(100), nullable=False)
    translation = db.Column(db.String(100), nullable=False)
    audio = db.Column(db.String(200), nullable=False)
    image = db.Column(db.String(200), nullable=False)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

def get_unique_filename(base_name, extension):
    counter = 1
    new_name = f"{base_name}_{counter}.{extension}"
    while Submission.query.filter_by(audio=new_name).first() or Submission.query.filter_by(image=new_name).first():
        counter += 1
        new_name = f"{base_name}_{counter}.{extension}"
    return new_name

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        word = request.form.get("word", "").strip()
        transit = request.form.get("transit", "").strip() or request.form.get("suggested", "").strip()
        translation = request.form.get("translation", "").strip()
        audio = request.files.get("audio")
        image = request.files.get("image")

        if not word or not transit or not translation or not audio or not image:
            flash("All fields are required!", "danger")
            return redirect(url_for("index"))

        safe_word = secure_filename(word)
        audio_filename = get_unique_filename(safe_word, "webm")
        image_filename = get_unique_filename(safe_word, "jpg")

        audio_path = os.path.join(app.config['UPLOAD_FOLDER'], audio_filename)
        image_path = os.path.join(app.config['UPLOAD_FOLDER'], image_filename)

        audio.save(audio_path)
        image.save(image_path)

        new_entry = Submission(word=word, transit=transit, translation=translation, audio=audio_filename, image=image_filename)
        db.session.add(new_entry)
        db.session.commit()

        flash("Upload successful!", "success")
        return redirect(url_for("index"))

    return render_template("index.html")

@app.route("/translate", methods=["POST"])
def translate_text():
    data = request.json
    kannada_word = data.get("word", "").strip()

    if not kannada_word:
        return jsonify({"translation": "", "transliteration": ""})

    try:
        # Kannada to English Translation
        translated_text = GoogleTranslator(source="kn", target="en").translate(kannada_word)

        # Fetch Transliteration from Google Translate API
        translit_url = f"https://translate.googleapis.com/translate_a/single?client=gtx&sl=kn&tl=en&dt=rm&q={kannada_word}"
        response = requests.get(translit_url).json()

        # Extract Transliteration (if available)
        transliteration = response[0][0][1] if response and response[0][0][1] else ""

        return jsonify({"translation": translated_text, "transliteration": transliteration})

    except Exception:
        return jsonify({"error": "Translation failed. Try again later."})

@app.route("/transliterate", methods=["POST"])
def transliterate_text():
    data = request.json
    kannada_word = data.get("word", "").strip()

    if not kannada_word:
        return jsonify({"transit": ""})

    try:
        # Use 'kannada' as the source script
        transit_text = transliterate(kannada_word, 'kannada', ITRANS)  
        return jsonify({"transit": transit_text})
    except Exception as e:
        print("Transliteration Error:", str(e))
        return jsonify({"transit": ""})

@app.route("/database")
def view_database():
    entries = Submission.query.all()  # Fetch all entries from the database
    return render_template("database.html", data=entries)

@app.route("/recognize_audio", methods=["POST"])
def recognize_audio():
    audio_file = request.data  # Get the audio blob from the frontend
    audio_path = "temp_audio.wav"

    with open(audio_path, "wb") as f:
        f.write(audio_file)

    # Convert audio format if needed (e.g., from webm to wav)
    try:
        sound = AudioSegment.from_file(audio_path, format="webm")
        sound.export(audio_path, format="wav")
    except:
        return jsonify({"error": "Audio conversion failed"}), 500

    # Recognize speech
    recognizer = sr.Recognizer()
    with sr.AudioFile(audio_path) as source:
        audio = recognizer.record(source)

    try:
        recognized_word = recognizer.recognize_google(audio, language="kn-IN")
        print(f"Recognized Word: {recognized_word}")  # Debugging Output

        # Search database for recognized word
        entry = Submission.query.filter_by(word=recognized_word).first()
        if entry:
            return jsonify({
                "word": entry.word, 
                "translit": entry.transit, 
                "translation": entry.translation,
                "image": url_for('static', filename='uploads/' + entry.image), 
                "audio": url_for('static', filename='uploads/' + entry.audio)
            })

        return jsonify({"error": "Word not found"}), 404

    except sr.UnknownValueError:
        return jsonify({"error": "Could not understand audio"}), 400
    except sr.RequestError:
        return jsonify({"error": "Speech recognition service error"}), 500


if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=True)
