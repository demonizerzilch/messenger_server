# server.py
from flask import Flask, request, jsonify
import os, json

app = Flask(__name__)

# Make data folder
os.makedirs("data", exist_ok=True)

# Users storage
USERS_FILE = "data/users.json"
MESSAGES_FILE = "data/messages.json"

# Initialize files
for f, default in [(USERS_FILE, {}), (MESSAGES_FILE, {})]:
    if not os.path.exists(f):
        with open(f, "w") as file:
            json.dump(default, file)

# Helper functions
def load_json(file):
    with open(file, "r") as f:
        return json.load(f)

def save_json(file, data):
    with open(file, "w") as f:
        json.dump(data, f, indent=2)

# Create account
@app.route("/register", methods=["POST"])
def register():
    data = request.json
    users = load_json(USERS_FILE)
    username = data.get("username")
    password = data.get("password")
    if username in users:
        return jsonify({"status": "error", "message": "Username exists"}), 400
    users[username] = {"password": password, "friends": []}
    save_json(USERS_FILE, users)
    return jsonify({"status": "ok"})

# Login
@app.route("/login", methods=["POST"])
def login():
    data = request.json
    users = load_json(USERS_FILE)
    username = data.get("username")
    password = data.get("password")
    if username not in users or users[username]["password"] != password:
        return jsonify({"status": "error", "message": "Invalid login"}), 400
    return jsonify({"status": "ok"})

# Send friend request
@app.route("/add_friend", methods=["POST"])
def add_friend():
    data = request.json
    users = load_json(USERS_FILE)
    u1 = data.get("from")
    u2 = data.get("to")
    if u1 not in users or u2 not in users:
        return jsonify({"status": "error", "message": "User not found"}), 400
    if u2 not in users[u1]["friends"]:
        users[u1]["friends"].append(u2)
    if u1 not in users[u2]["friends"]:
        users[u2]["friends"].append(u1)
    save_json(USERS_FILE, users)
    return jsonify({"status": "ok"})

# Send message
@app.route("/send_message", methods=["POST"])
def send_message():
    data = request.json
    messages = load_json(MESSAGES_FILE)
    chat = data.get("chat")  # format: "user1_user2"
    if chat not in messages:
        messages[chat] = []
    messages[chat].append({"from": data["from"], "text": data["text"]})
    save_json(MESSAGES_FILE, messages)
    return jsonify({"status": "ok"})

# Get messages
@app.route("/get_messages/<chat>")
def get_messages(chat):
    messages = load_json(MESSAGES_FILE)
    return jsonify(messages.get(chat, []))

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
# ---------------- READY FOR RENDER/WSGI ----------------
# NOTE: No app.run() needed; Render handles this
