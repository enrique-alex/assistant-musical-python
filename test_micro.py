import speech_recognition as sr

r = sr.Recognizer()

with sr.Microphone() as source:
    print("🎤 Dis quelque chose...")
    audio = r.listen(source)

try:
    texte = r.recognize_google(audio, language="fr-FR")
    print("Tu as dit :", texte)
except sr.UnknownValueError:
    print("🤷 Je n'ai pas compris.")
except sr.RequestError:
    print("⚠️ Problème de connexion au service Google.")
