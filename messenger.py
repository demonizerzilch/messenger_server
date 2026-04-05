# messenger.py
import tkinter as tk
from tkinter import simpledialog, scrolledtext, messagebox
import requests

SERVER_URL = "https://popcornmiku.onrender.com"  # your live server

username = ""
chat_with = ""

# Login or register
def login():
    global username
    username = simpledialog.askstring("Login", "Enter username:")
    password = simpledialog.askstring("Login", "Enter password:", show="*")
    try:
        r = requests.post(f"{SERVER_URL}/login", json={"username": username, "password": password})
        if r.json().get("status") != "ok":
            # Try registering
            r2 = requests.post(f"{SERVER_URL}/register", json={"username": username, "password": password})
            if r2.json().get("status") == "ok":
                messagebox.showinfo("Registered", f"Account {username} created!")
            else:
                messagebox.showerror("Error", "Cannot login or register")
    except Exception as e:
        messagebox.showerror("Error", f"Cannot connect to server: {e}")

login()

# GUI
root = tk.Tk()
root.title(f"Messenger - {username}")
root.geometry("400x600")

chat_box = scrolledtext.ScrolledText(root)
chat_box.pack(expand=True, fill="both")

entry = tk.Entry(root)
entry.pack(fill="x")

def send_message():
    global chat_with
    if not chat_with:
        chat_with = simpledialog.askstring("Chat with", "Enter username to chat with:")
    text = entry.get()
    if not text.strip():
        return
    entry.delete(0, tk.END)
    requests.post(f"{SERVER_URL}/send_message", json={"from": username, "chat": f"{username}_{chat_with}", "text": text})
    update_messages()

def update_messages():
    global chat_with
    if not chat_with:
        return
    try:
        r = requests.get(f"{SERVER_URL}/get_messages/{username}_{chat_with}")
        chat_box.delete(1.0, tk.END)
        for m in r.json():
            chat_box.insert(tk.END, f"{m['from']}: {m['text']}\n")
    except:
        chat_box.insert(tk.END, "Cannot connect to server\n")
    root.after(2000, update_messages)

entry.bind("<Return>", lambda e: send_message())
update_messages()
root.mainloop()
