# server.py
from flask import Flask, request, jsonify
import os, json
from datetime import datetime

app = Flask(__name__)

# ---------------- CONFIG ----------------
DATA_DIR = "data"
USERS_FILE = os.path.join(DATA_DIR, "users.json")
CHANNELS_FILE = os.path.join(DATA_DIR, "channels.json")
AVATAR_DIR = os.path.join(DATA_DIR, "avatars")

# Create folders if missing
for folder in [DATA_DIR, AVATAR_DIR]:
    os.makedirs(folder, exist_ok=True)

# ---------------- HELPERS ----------------
def load_json(path, default={}):
    if os.path.exists(path):
        with open(path, "r") as f:
            return json.load(f)
    return default

def save_json(path, data):
    with open(path, "w") as f:
        json.dump(data, f, indent=4)

# Load data
users = load_json(USERS_FILE)
channels = load_json(CHANNELS_FILE, {"general":[]})

# ---------------- ROUTES ----------------
# ----- Users -----
@app.route("/register", methods=["POST"])
def register():
    u = request.json["username"]
    p = request.json["password"]
    if u in users:
        return jsonify({"status":"error","msg":"Username taken"})
    users[u] = {"password":p, "avatar":None,"friends":[],"requests":[]}
    save_json(USERS_FILE, users)
    return jsonify({"status":"ok"})

@app.route("/login", methods=["POST"])
def login():
    u = request.json["username"]
    p = request.json["password"]
    if u in users and users[u]["password"] == p:
        return jsonify({"status":"ok","avatar":users[u]["avatar"],"channels":list(channels.keys())})
    return jsonify({"status":"error","msg":"Invalid credentials"})

@app.route("/update_avatar", methods=["POST"])
def update_avatar():
    u = request.json["username"]
    users[u]["avatar"] = request.json.get("avatar")
    save_json(USERS_FILE, users)
    return jsonify({"status":"ok"})

# ----- Friends -----
@app.route("/add_friend", methods=["POST"])
def add_friend():
    sender = request.json["from"]
    target = request.json["to"]
    if target in users:
        if sender not in users[target]["requests"]:
            users[target]["requests"].append(sender)
        save_json(USERS_FILE, users)
        return jsonify({"status":"sent"})
    return jsonify({"status":"error"})

@app.route("/accept_friend", methods=["POST"])
def accept_friend():
    user = request.json["user"]
    friend = request.json["friend"]
    if friend not in users[user]["friends"]:
        users[user]["friends"].append(friend)
    if user not in users[friend]["friends"]:
        users[friend]["friends"].append(user)
    if friend in users[user]["requests"]:
        users[user]["requests"].remove(friend)
    save_json(USERS_FILE, users)
    return jsonify({"status":"ok"})

# ----- Channels & Messages -----
@app.route("/create_channel", methods=["POST"])
def create_channel():
    ch = request.json["channel"]
    if ch not in channels:
        channels[ch] = []
        save_json(CHANNELS_FILE, channels)
    return jsonify({"status":"ok"})

@app.route("/send_message", methods=["POST"])
def send_message():
    ch = request.json["channel"]
    msg = request.json
    if ch not in channels:
        channels[ch] = []
    channels[ch].append(msg)
    save_json(CHANNELS_FILE, channels)
    return jsonify({"status":"ok"})

@app.route("/get_messages/<channel>", methods=["GET"])
def get_messages(channel):
    return jsonify(channels.get(channel, []))

# ----- Avatars -----
@app.route("/avatars/<filename>")
def avatars(filename):
    return send_from_directory(AVATAR_DIR, filename)

# ---------------- READY FOR RENDER/WSGI ----------------
# NOTE: No app.run() needed; Render handles this
