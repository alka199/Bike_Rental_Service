import speech_recognition as sr

r = sr.Recognizer()
with sr.Microphone() as source:
# read the audio from the default microphone

    audio_data = r.record(source,duration=5)
    print("Recognizing...")
     # convert speech to text
    text = r.recognize_google(audio_data)
    # text = r.recognize-google (audio_data, language="")
    print(text)