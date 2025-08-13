from flask import Flask, jsonify, send_file
from flask_cors import CORS
import os

app = Flask(__name__)
CORS(app)

# ✅ UptimeRobot ping
@app.route("/")
def home():
    return jsonify({"status": "ok"})

# 📦 Выгрузка текущего JSON-файла
@app.route("/get-json")
def get_json():
    json_path = "tracks.json"
    if os.path.exists(json_path):
        return send_file(json_path, mimetype="application/json")
    else:
        return jsonify({"error": "tracks.json not found"}), 404

@app.route("/check-tracks", methods=["POST"])
def check_tracks():
    import json
    ids = request.json.get("ids", [])
    with open("tracks.json", "r") as f:
        tracks = json.load(f)
    result = [track_id in tracks for track_id in ids]
    return jsonify(result)

@app.route("/add-track", methods=["POST"])
def add_track_route():
    import json
    data = request.json
    track_id = data["id"]
    url = data["url"]
    title = data["title"]
    artist = data["artist"]
    with open("tracks.json", "r") as f:
        tracks = json.load(f)
    if track_id in tracks:
        return jsonify({"error": "Track already exists"}), 400
    tracks[track_id] = [track_id, url, title, artist]
    with open("tracks.json", "w") as f:
        json.dump(tracks, f, indent=2)
    return jsonify({"status": "Track added"})

@app.route("/delete-track", methods=["POST"])
def delete_track_route():
    import json
    track_id = request.json.get("id")
    with open("tracks.json", "r") as f:
        tracks = json.load(f)
    if track_id not in tracks:
        return jsonify({"error": "Track not found"}), 404
    del tracks[track_id]
    with open("tracks.json", "w") as f:
        json.dump(tracks, f, indent=2)
    return jsonify({"status": "Track deleted"})

def track_exists(track_id):
    import json
    with open("tracks.json", "r") as f:
        tracks = json.load(f)
    return track_id in tracks

@app.route("/add-track", methods=["POST"])
def add_track_auto():
    import json
    data = request.get_json()
    url = data.get("url")
    title = data.get("title")
    artist = data.get("artist")

    if not all([url, title, artist]):
        return jsonify({"error": "Missing fields"}), 400

    path = "tracks.json"
    if os.path.exists(path):
        with open(path, "r", encoding="utf-8") as f:
            try:
                tracks = json.load(f)
            except json.JSONDecodeError:
                tracks = {}
    else:
        tracks = {}

    new_id = str(get_free_index())
    tracks[new_id] = [new_id, url, title, artist]

    with open(path, "w", encoding="utf-8") as f:
        json.dump(tracks, f, indent=2)

    return jsonify({"status": "Track added", "id": new_id})

def delete_track(track_id):
    import json
    with open("tracks.json", "r") as f:
        tracks = json.load(f)
    if track_id not in tracks:
        return {"error": "Track not found"}
    del tracks[track_id]
    with open("tracks.json", "w") as f:
        json.dump(tracks, f, indent=2)
    return {"status": "Track deleted"}

def get_free_index():
    import json, os
    path = "tracks.json"
    if not os.path.exists(path):
        return 0
    with open(path, "r", encoding="utf-8") as f:
        try:
            tracks = json.load(f)
        except json.JSONDecodeError:
            return 0
    used_ids = set(map(int, tracks.keys()))
    i = 0
    while i in used_ids:
        i += 1
    return i


if __name__ == "__main__":
    app.run(debug=True)
