from dotenv import load_dotenv
load_dotenv()
from flask import Flask, request, jsonify
from flask_cors import CORS
import os
import torchaudio
import torch
import soundfile as sf
from transformers import Wav2Vec2FeatureExtractor, Wav2Vec2ForSequenceClassification
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials



app = Flask(__name__)
CORS(app)

# Spotify 測試 API
@app.route('/spotify-test')
def spotify_test():
    client_id = os.environ.get("SPOTIFY_CLIENT_ID")
    client_secret = os.environ.get("SPOTIFY_CLIENT_SECRET")

    if not client_id or not client_secret:
        return jsonify({"error": "Missing Spotify credentials in .env"})

    sp = spotipy.Spotify(auth_manager=SpotifyClientCredentials(
        client_id=client_id,
        client_secret=client_secret
    ))

    result = sp.search(q="relaxing music", type="track", limit=3)
    return jsonify(result)

# Emotion model 載入
feature_extractor = Wav2Vec2FeatureExtractor.from_pretrained("xmj2002/hubert-base-ch-speech-emotion-recognition")
model = Wav2Vec2ForSequenceClassification.from_pretrained("xmj2002/hubert-base-ch-speech-emotion-recognition")

emotion_labels = ['anger', 'fear', 'happy', 'neutral', 'sad', 'surprise']

# Upload audio API
@app.route('/upload-audio', methods=['POST'])
def upload_audio():
    if 'file' not in request.files:
        return jsonify({'error': 'No file part in the request'}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400
    
    temp_path = '/tmp/temp_audio.wav'
    file.save(temp_path)
    
    speech_array, sampling_rate = sf.read(temp_path)
    
    inputs = feature_extractor(speech_array, sampling_rate=sampling_rate, return_tensors="pt", padding=True)
    with torch.no_grad():
        logits = model(**inputs).logits
    predicted_id = torch.argmax(logits, dim=-1).item()
    predicted_emotion = emotion_labels[predicted_id]
    
    return jsonify({'emotion': predicted_emotion})

# Home route
@app.route('/')
def home():
    return "🎵 Emotion Music Recommender API is running!"

# Run app
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
