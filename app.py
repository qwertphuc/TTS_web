from flask import Flask, render_template, send_from_directory, request, jsonify
import os
import time
import threading
from tts import process_text_with_flow, process_text_without_flow  # Import TTS functions
from flask_cors import CORS
from auth import require_api_key

app = Flask(__name__)
CORS(app, resources={r"/api/*": {"origins": "*"}})

# Configure media folders
MEDIA_FOLDER = 'media'
SHORT_MEDIA_FOLDER = os.path.join(MEDIA_FOLDER, 'short')
LONG_MEDIA_FOLDER = os.path.join(MEDIA_FOLDER, 'long')
TRASH_FOLDER = os.path.join(MEDIA_FOLDER, 'trash')

# Create media folders if they don't exist
os.makedirs(SHORT_MEDIA_FOLDER, exist_ok=True)
os.makedirs(LONG_MEDIA_FOLDER, exist_ok=True)
os.makedirs(TRASH_FOLDER, exist_ok=True)

# Time to delete files (N minutes)
DELETE_TIME = 1 * 60  # N minutes

# Function to clean up old files
def cleanup_old_files():
    while True:
        time.sleep(DELETE_TIME)
        now = time.time()
        for folder in [SHORT_MEDIA_FOLDER, LONG_MEDIA_FOLDER, TRASH_FOLDER]:
            for filename in os.listdir(folder):
                file_path = os.path.join(folder, filename)
                if os.path.isfile(file_path):
                    file_age = now - os.path.getmtime(file_path)
                    if file_age > DELETE_TIME:
                        os.remove(file_path)
                        print(f"Deleted {file_path}")

# Start the cleanup thread
cleanup_thread = threading.Thread(target=cleanup_old_files)
cleanup_thread.daemon = True
cleanup_thread.start()

# API to serve static files
@app.route('/media/<storage_type>/<filename>')
def media(storage_type, filename):
    if storage_type == 'short':
        directory = SHORT_MEDIA_FOLDER
    elif storage_type == 'long':
        directory = LONG_MEDIA_FOLDER
    elif storage_type == 'trash':
        directory = TRASH_FOLDER
    else:
        return jsonify({"error": "Invalid storage type"}), 400
    return send_from_directory(directory, filename)

# API to handle TTS processing
@app.route('/api/short', methods=['POST'])
def short_storage():
    return process_tts(request, SHORT_MEDIA_FOLDER)

@app.route('/api/long', methods=['POST'])
@require_api_key
def long_storage():
    return process_tts(request, LONG_MEDIA_FOLDER)

def process_tts(request, storage_folder):
    data = request.form
    text = data.get('text')
    voice = data.get('voice')
    enable_flow = data.get('enableFlow') == 'true'

    if not text or not voice:
        return jsonify({"error": "Missing text or voice parameter"}), 400

    # Process the text using the appropriate TTS function
    if enable_flow:
        filename, file_path = process_text_with_flow(text, voice, storage_folder)
    else:
        filename, file_path = process_text_without_flow(text, voice, storage_folder)

    # Return the URL of the final audio file
    audio_url = f"/media/{os.path.basename(storage_folder)}/{filename}"
    return jsonify({"audioUrl": audio_url})

# API to delete a file
@app.route('/api/delete', methods=['DELETE'])
def delete_file():
    filename = request.args.get('file')
    if not filename:
        return jsonify({"error": "Missing filename parameter"}), 400

    file_path = os.path.join(TRASH_FOLDER, filename)
    if os.path.exists(file_path):
        os.remove(file_path)
        return jsonify({"message": f"Deleted {filename}"}), 200
    else:
        return jsonify({"error": "File not found"}), 404

# API to list chunked audio files
@app.route('/api/chunked-audio', methods=['GET'])
def list_chunked_audio():
    chunked_files = [f for f in os.listdir(TRASH_FOLDER) if f.startswith("chunk_")]
    return jsonify({"chunkedFiles": chunked_files})

# Homepage
@app.route('/')
def index():
    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True)