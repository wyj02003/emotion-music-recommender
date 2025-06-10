from flask import Flask, request, jsonify
from flask_cors import CORS
import os

app = Flask(__name__)
CORS(app)

# 測試用 API
@app.route('/')
def home():
    return "🎵 Emotion Music Recommender API is running!"

# Spotify 測試 API（用你的 client_id/client_secret）
@app.route('/spotify-test')
def spotify_test():
    import spotipy
    from spotipy.oauth2 import SpotifyClientCredentials

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

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
