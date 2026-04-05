# messenger.py
import tkinter as tk
from tkinter import simpledialog, scrolledtext
import requests

SERVER_URL = "https://popcornmiku.onrender.com"  # <- replace with your Render URL

username = ""
chat_with = ""

# Login / register
def login():
    global username
    username = simpledialog.askstring("Login", "Enter username:")
    password = simpledialog.askstring("Login", "Enter password:", show="*")
    r = requests.post(f"{SERVER_URL}/login", json={"username": username, "password": password})
    if r.json().get("status") != "ok":
        # Try register
        r2 = requests.post(f"{SERVER_URL}/register", json={"username": username, "password": password})
        if r2.json().get("status") == "ok":
            tk.messagebox.showinfo("Registered", f"Account {username} created!")
        else:
            tk.messagebox.showerror("Error", "Cannot login or register")
login()

# GUI
root = tk.Tk()
root.title(f"Messenger - {username}")

chat_box = scrolledtext.ScrolledText(root)
chat_box.pack(expand=True, fill="both")

entry = tk.Entry(root)
entry.pack(fill="x")

def send_message():
    global chat_with
    if not chat_with:
        chat_with = simpledialog.askstring("Chat with", "Enter username to chat with:")
    text = entry.get()
    entry.delete(0, tk.END)
    requests.post(f"{SERVER_URL}/send_message", json={"from": username, "chat": f"{username}_{chat_with}", "text": text})
    update_messages()

def update_messages():
    global chat_with
    if not chat_with:
        return
    r = requests.get(f"{SERVER_URL}/get_messages/{username}_{chat_with}")
    chat_box.delete(1.0, tk.END)
    for m in r.json():
        chat_box.insert(tk.END, f"{m['from']}: {m['text']}\n")
    root.after(2000, update_messages)

entry.bind("<Return>", lambda e: send_message())
update_messages()
root.mainloop()
