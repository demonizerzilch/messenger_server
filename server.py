# server.py
from flask import Flask, request, jsonify
import os, json

app = Flask(__name__)

# Auto-create data folder
os.makedirs("data", exist_ok=True)

USERS_FILE = "data/users.json"
MESSAGES_FILE = "data/messages.json"

# Initialize JSON files if missing
for f, default in [(USERS_FILE, {}), (MESSAGES_FILE, {})]:
    if not os.path.exists(f):
        with open(f, "w") as file:
            json.dump(default, file)

# Homepage so 404 won't happen
@app.route("/")
def home():
    return "POPCORNMIKU Messenger Server is running!"

# Register
@app.route("/register", methods=["POST"])
def register():
    data = request.json
    users = json.load(open(USERS_FILE))
    u = data["username"]
    if u in users:
        return jsonify({"status": "error", "message": "Username exists"}), 400
    users[u] = {"password": data["password"], "friends": []}
    json.dump(users, open(USERS_FILE, "w"), indent=2)
    return jsonify({"status": "ok"})

# Login
@app.route("/login", methods=["POST"])
def login():
    data = request.json
    users = json.load(open(USERS_FILE))
    u = data["username"]
    if u not in users or users[u]["password"] != data["password"]:
        return jsonify({"status": "error"}), 400
    return jsonify({"status": "ok"})

# Add friend
@app.route("/add_friend", methods=["POST"])
def add_friend():
    data = request.json
    users = json.load(open(USERS_FILE))
    u1 = data["from"]
    u2 = data["to"]
    if u1 not in users or u2 not in users:
        return jsonify({"status": "error"}), 400
    if u2 not in users[u1]["friends"]:
        users[u1]["friends"].append(u2)
    if u1 not in users[u2]["friends"]:
        users[u2]["friends"].append(u1)
    json.dump(users, open(USERS_FILE, "w"), indent=2)
    return jsonify({"status": "ok"})

# Send message
@app.route("/send_message", methods=["POST"])
def send_message():
    data = request.json
    messages = json.load(open(MESSAGES_FILE))
    chat = data["chat"]  # "user1_user2"
    if chat not in messages:
        messages[chat] = []
    messages[chat].append({"from": data["from"], "text": data["text"]})
    json.dump(messages, open(MESSAGES_FILE, "w"), indent=2)
    return jsonify({"status": "ok"})

# Get messages
@app.route("/get_messages/<chat>")
def get_messages(chat):
    messages = json.load(open(MESSAGES_FILE))
    return jsonify(messages.get(chat, []))

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
