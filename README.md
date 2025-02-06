# Audio Recognition and Translation Project

## Overview
This project provides a web application where users can upload words in Kannada, their corresponding English transliterations, translations, and audio recordings. The application stores these details in a database, and users can view the stored data along with audio and image files. The application also supports transliterating Kannada text to English form using the Indic Transliteration API and Google Translate API for translation.

## Features
- **Upload Kannada Word:** Users can input a Kannada word, its transliteration in English, and its translation.
- **Audio Recording:** Users can upload an audio file that corresponds to the Kannada word.
- **Image Upload:** Users can upload an image that corresponds to the Kannada word.
- **Database View:** Users can view all the stored data in a database, with the option to listen to the audio and view the image.
- **Transliteration & Translation:** The system auto-generates an English transliteration of the Kannada word and translates it into English.

## Requirements
1. Python 3.x
2. Flask
3. SQLAlchemy
4. Google Translate API
5. Indic Transliteration API
6. pydub - for audio file format conversion

## Project Structure
```
audio_project_V1/
│
├── app.py                # Main Flask application
├── templates/
│   ├── index.html        # HTML form for uploading data
│   ├── database.html     # View database page (displays stored words)
├── static/
│   └── uploads/          # Folder to store uploaded images and audio files
├── requirements.txt      # List of required Python libraries
└── README.md             # This readme file
```

## Setup Instructions

1. Clone the repository:
   ```
   git clone <repository-url>
   cd <project_directory>
   ```

2. Set up a virtual environment:
   ```
   python -m venv venv
   # On Windows
   venv\Scripts\activate
   # On macOS/Linux
   source venv/bin/activate

   ```

3. Install the required packages:
   ```
   pip install -r requirements.txt
   ```

4. Set up the database:
   ```
   flask db init
   flask db migrate
   flask db upgrade
   ```

## Usage
1. Run the application:
   ```
   flask run
   ```

2. Open your web browser and navigate to `http://127.0.0.1:5000/`.

## Contributing
Contributions are welcome! Please submit a pull request or open an issue for any suggestions or improvements.

## License
This project is licensed under the MIT License. See the LICENSE file for details.