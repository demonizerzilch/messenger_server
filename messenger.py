# messenger.py
import tkinter as tk
from tkinter import simpledialog, messagebox, scrolledtext
import requests
import threading
import time

SERVER_URL = "https://popcornmiku.onrender.com"  # replace with your Render URL

username = ""
current_channel = "general"

# ---------------- GUI ----------------
root = tk.Tk()
root.title("Messenger")
root.geometry("600x500")

messages_box = scrolledtext.ScrolledText(root, state="disabled")
messages_box.pack(expand=True, fill="both")

entry = tk.Entry(root)
entry.pack(fill="x")

def refresh_messages():
    while True:
        if current_channel:
            try:
                r = requests.get(f"{SERVER_URL}/get_messages/{current_channel}")
                if r.status_code == 200:
                    msgs = r.json()
                    messages_box.config(state="normal")
                    messages_box.delete(1.0, tk.END)
                    for m in msgs:
                        messages_box.insert(tk.END, f"{m['user']}: {m['message']}\n")
                    messages_box.config(state="disabled")
            except:
                pass
        time.sleep(2)

def send_message(event=None):
    msg = entry.get()
    if msg:
        try:
            requests.post(f"{SERVER_URL}/send_message", json={
                "channel": current_channel,
                "user": username,
                "message": msg
            })
        except:
            messagebox.showerror("Error","Cannot send message")
        entry.delete(0, tk.END)

entry.bind("<Return>", send_message)

# ---------------- Login ----------------
def login_prompt():
    global username
    username = simpledialog.askstring("Login", "Enter username:")
    password = simpledialog.askstring("Login", "Enter password:", show="*")
    r = requests.post(f"{SERVER_URL}/login", json={"username":username,"password":password})
    if r.status_code == 200 and r.json().get("status")=="ok":
        threading.Thread(target=refresh_messages, daemon=True).start()
    else:
        messagebox.showerror("Error","Login failed")
        root.destroy()

login_prompt()
root.mainloop()