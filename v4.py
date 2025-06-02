import tkinter as tk
from tkinter import scrolledtext, messagebox, simpledialog
import pyttsx3
import speech_recognition as sr
import datetime
import wikipedia
import webbrowser
import os
import pymongo
import threading

# --- MongoDB Atlas Setup ---
client = pymongo.MongoClient("mongodb+srv://useradmin:admin@cluster0.lozjltu.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0")
db = client["jarvisDB"]
history_col = db["history"]
memory_col = db["memory"]
history_col.create_index([("timestamp", pymongo.DESCENDING)])
memory_col.create_index([("timestamp", pymongo.DESCENDING)])

# Initialize speech engine
engine = pyttsx3.init()
engine.setProperty('rate', 160)
engine.setProperty('voice', engine.getProperty('voices')[1].id)

def speak(text):
    engine.say(text)
    engine.runAndWait()

def update_display(text):
    root.after(0, lambda: output_area.insert(tk.END, text + "\n"))
    root.after(0, lambda: output_area.see(tk.END))

def save_history(text):
    threading.Thread(target=lambda: history_col.insert_one({"entry": text, "timestamp": datetime.datetime.now()})).start()

def save_note():
    note = simpledialog.askstring("Memory", "What would you like me to remember?")
    if note:
        memory_col.insert_one({"note": note, "timestamp": datetime.datetime.now()})
        update_display(f"📌 Noted: {note}")
        speak("Noted.")

def show_history():
    def task():
        records = history_col.find().sort("timestamp", -1)
        history_list = [f"{rec['timestamp'].strftime('%Y-%m-%d %H:%M:%S')} - {rec['entry']}" for rec in records]
        messagebox.showinfo("History", "\n".join(history_list) if history_list else "No history yet.")
    threading.Thread(target=task).start()

def show_notes():
    def task():
        records = memory_col.find().sort("timestamp", -1)
        notes_list = [f"{rec['timestamp'].strftime('%Y-%m-%d %H:%M:%S')} - {rec['note']}" for rec in records]
        messagebox.showinfo("Notes", "\n".join(notes_list) if notes_list else "No notes yet.")
    threading.Thread(target=task).start()

def take_command():
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        update_display("🌊 Listening... [~ ~ ~]")
        audio = recognizer.listen(source)
    try:
        query = recognizer.recognize_google(audio)
        update_display(f"🗣️ You: {query}")
        save_history(f"You: {query}")
        return query.lower()
    except:
        update_display("❌ Couldn't understand.")
        return ""

def handle_command():
    def process():
        query = take_command()
        if not query:
            return

        if 'time' in query:
            now = datetime.datetime.now().strftime('%H:%M:%S')
            response = f"It's {now}"
        elif 'date' in query:
            date = datetime.date.today().strftime('%B %d, %Y')
            response = f"Today is {date}"
        elif 'notepad' in query:
            os.system('notepad')
            response = "Opening Notepad"
        elif 'wikipedia' in query:
            speak("Searching Wikipedia...")
            try:
                result = wikipedia.summary(query.replace("wikipedia", ""), sentences=2)
                response = f"According to Wikipedia: {result}"
            except:
                response = "Couldn't find that."
        elif 'search' in query:
            topic = query.replace("search", "")
            webbrowser.open(f"https://www.google.com/search?q={topic}")
            response = f"Searching Google for {topic}"
        elif 'open' in query:
            keyword = query.replace("open", "").strip()
            if "chrome" in keyword:
                os.system("start chrome")
                response = "Opening Chrome"
            elif "file" in keyword or "folder" in keyword:
                os.startfile("C:\\")  # Opens C Drive
                response = "Opening File Explorer"
            else:
                response = f"Trying to open {keyword}"
                os.system(f"start {keyword}")
        elif 'exit' in query:
            speak("Goodbye!")
            root.destroy()
            return
        else:
            response = "I'm not sure, but here's what I found."
            webbrowser.open(f"https://www.google.com/search?q={query}")

        update_display(f"🤖 {response}")
        speak(response)
        save_history(f"Assistant: {response}")

    threading.Thread(target=process).start()

def exit_app():
    speak("Goodbye!")
    root.destroy()

# --- GUI Setup ---
root = tk.Tk()
root.title("🧠 JARVIS-X AI Assistant")
root.geometry("720x640")
root.config(bg="#0f0f0f")

title = tk.Label(root, text="🔴 JARVIS-X", font=("Consolas", 24, "bold"), bg="#0f0f0f", fg="#00ffcc")
title.pack(pady=10)

output_area = scrolledtext.ScrolledText(root, wrap=tk.WORD, width=75, height=20, font=("Consolas", 12),
                                        bg="#1e1e1e", fg="#00ff00", insertbackground="white", borderwidth=0)
output_area.pack(pady=10)

button_frame = tk.Frame(root, bg="#0f0f0f")
button_frame.pack(pady=10)

btn_listen = tk.Button(button_frame, text="🎧 Listen", command=handle_command,
                       font=("Consolas", 13), bg="#ff0040", fg="white", width=12)
btn_listen.grid(row=0, column=0, padx=10)

btn_note = tk.Button(button_frame, text="📌 Remember", command=save_note,
                     font=("Consolas", 13), bg="#222", fg="white", width=12)
btn_note.grid(row=0, column=1, padx=10)

btn_history = tk.Button(button_frame, text="📂 History", command=show_history,
                        font=("Consolas", 13), bg="#222", fg="white", width=12)
btn_history.grid(row=0, column=2, padx=10)

btn_notes = tk.Button(button_frame, text="📖 Notes", command=show_notes,
                      font=("Consolas", 13), bg="#222", fg="white", width=12)
btn_notes.grid(row=0, column=3, padx=10)

btn_exit = tk.Button(root, text="❌ Exit", command=exit_app, font=("Consolas", 13), bg="#222", fg="white", width=15)
btn_exit.pack(pady=10)

suggest = tk.Label(root, text="💡 Try: What's the time? | Wikipedia Elon Musk | Open Notepad | Search AI", font=("Consolas", 10),
                   fg="#888", bg="#0f0f0f")
suggest.pack(pady=5)

update_display("🤖 Welcome to your personal assistant.\nClick '🎧 Listen' and speak a command...")

root.mainloop()
