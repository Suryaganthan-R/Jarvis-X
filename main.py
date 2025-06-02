import pyttsx3
import speech_recognition as sr
import webbrowser
import datetime
import wikipedia
import os
import requests


engine = pyttsx3.init()


engine.setProperty('rate', 150)


voices = engine.getProperty('voices')
for voice in voices:
    if "female" in voice.name.lower():
        engine.setProperty('voice', voice.id)
        break

# speak function
def speak(text):
    engine.say(text)
    engine.runAndWait()

# listen to user's command
def take_command():
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        print("Listening...")
        audio = recognizer.listen(source)
    try:
        command = recognizer.recognize_google(audio)
        print("You said:", command)
        return command.lower()
    except sr.UnknownValueError:
        speak("Sorry, I didn't catch that.")
        return ""
    except sr.RequestError:
        speak("Could not connect to the speech service.")
        return ""
    
# main function
def main():
    speak("Hello! I am your voice assistant. How can I help you?")
    while True:
        query = take_command()
        
        if 'time' in query:
            now = datetime.datetime.now().strftime('%H:%M:%S')
            speak(f"The current time is {now}")

        elif 'open' in query:
            if 'browser' in query or 'chrome' in query:
                speak("Opening browser")
                webbrowser.open('https://www.google.com')
            elif 'notepad' in query:
                speak("Opening Notepad")
                os.system('notepad')
            else:
                speak("I am not sure which software you want to open.")
            
        elif 'wikipedia' in query:
            speak("Searching Wikipedia...")
            query = query.replace('wikipedia', '')
            results = wikipedia.summary(query, sentences=2)
            speak(f"According to Wikipedia: {results}")

        elif 'search' in query or 'google' in query:
            speak("What should I search for?")
            search_query = take_command()
            webbrowser.open(f'https://www.google.com/search?q={search_query}')
            speak("Here are your search results.")

        elif 'play' in query and 'youtube' in query:
            speak("What should I play on YouTube?")
            song_name = take_command()
            webbrowser.open(f"https://www.youtube.com/results?search_query={song_name}")
            speak(f"Playing {song_name} on YouTube.")

        elif 'exit' in query or 'stop' in query:
            speak("Goodbye! Have a great day.")
            break

        else:
            speak("I am not sure about that. Let me search the web.")
            webbrowser.open(f'https://www.google.com/search?q={query}')

if __name__ == '__main__':
    main()



