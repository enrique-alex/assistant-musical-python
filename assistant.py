import os
import pygame
import speech_recognition as sr
import pyttsx3
import time
import re
import lyricsgenius
import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk
from mutagen.mp3 import MP3

# Initialisation des moteurs
engine = pyttsx3.init()
engine.setProperty("rate", 150)
pygame.init()
pygame.mixer.init()

# Dossier musique
MUSIC_FOLDER = os.path.join(os.path.dirname(__file__), "Musique")
musics = [f for f in os.listdir(MUSIC_FOLDER) if f.endswith(".mp3")]

# Variables de contrôle
index_actuel = 0
en_pause = False

# Fonctions
def parler(texte):
    print("Assistant :", texte)
    engine.say(texte)
    engine.runAndWait()

def ecouter():
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        parler("J'écoute...")
        audio = recognizer.listen(source)
    try:
        commande = recognizer.recognize_google(audio, language="fr-FR")
        print("Tu as dit :", commande)
        return commande.lower()
    except sr.UnknownValueError:
        parler("Je n'ai pas compris, peux-tu répéter ?")
        return None
    except sr.RequestError:
        parler("Erreur réseau.")
        return None

def jouer_musique(index):
    global index_actuel, en_pause
    index_actuel = index
    en_pause = False
    fichier = os.path.join(MUSIC_FOLDER, musics[index])
    pygame.mixer.music.load(fichier)
    pygame.mixer.music.play()
    parler(f"Lecture de {musics[index]}")


# Remplace ceci par ton vrai token
GENIUS_TOKEN = "79xG1kmBO9ipppHm24ArE_lVLMOP4kONI3iqZr2nEDsWrjFhf5xbTjlDnSA9o727"
genius = lyricsgenius.Genius(GENIUS_TOKEN)

def afficher_lyrics(titre):
    try:
        song = genius.search_song(titre)
        if song:
            fenetre_lyrics = tk.Toplevel()
            fenetre_lyrics.title(f"Paroles - {titre}")
            fenetre_lyrics.geometry("600x600")
            texte = tk.Text(fenetre_lyrics, wrap=tk.WORD, bg="#f2f2f2", font=("Segoe UI", 11))
            texte.insert(tk.END, song.lyrics)
            texte.config(state=tk.DISABLED)
            texte.pack(expand=True, fill=tk.BOTH)
        else:
            parler("Paroles introuvables.")
    except Exception as e:
        print("Erreur lyrics :", e)
        parler("Une erreur est survenue lors de la récupération des paroles.")


class MusicAssistantApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("PyGroove")
        self.geometry("950x800")
        self.configure(bg="#222831")
        self.resizable(False, False)

        style = ttk.Style(self)
        style.theme_use("clam")
        style.configure("TButton", font=("Segoe UI", 12), padding=10, background="#393E46", foreground="#EEEEEE")
        style.configure("TLabel", background="#222831", foreground="#00ADB5", font=("Segoe UI", 14, "bold"))
        
                # === Logo ===
        logo_path = os.path.join(os.path.dirname(__file__), "pygroove_logo.png")
        logo_image = Image.open(logo_path)
        logo_image = logo_image.resize((120, 120))  # Adapter la taille
        self.logo_photo = ImageTk.PhotoImage(logo_image)
        self.label_logo = tk.Label(self, image=self.logo_photo, bg="#222831")
        self.label_logo.pack(pady=(10, 5))

        self.label_title = ttk.Label(self, text="Pygroove", font=("Segoe UI", 18, "bold"))
        self.label_title.pack(pady=10)

        self.label_current = ttk.Label(self, text="Lecture : Aucun", font=("Segoe UI", 14))
        self.label_current.pack(pady=5)
        
        self.label_time = ttk.Label(self, text="00:00 / 00:00", font=("Segoe UI", 12))
        self.label_time.pack(pady=2)
        
        self.btn_lyrics = ttk.Button(self, text="📖 Paroles", command=self.show_lyrics)
        self.btn_lyrics.pack(pady=10)


        self.progress_var = tk.DoubleVar(value=0)
        self.progress_bar = ttk.Scale(self, from_=0, to=100, orient=tk.HORIZONTAL, variable=self.progress_var, length=400, state="disabled")
        self.progress_bar.pack(pady=2)
        self.after(1000, self.update_time)

        self.listbox = tk.Listbox(self, font=("Segoe UI", 12), bg="#393E46", fg="#EEEEEE", selectbackground="#00ADB5", height=10)
        for i, music in enumerate(musics):
            self.listbox.insert(tk.END, f"{i+1}. {music}")
        self.listbox.pack(pady=10, fill=tk.X, padx=30)
        self.listbox.bind("<<ListboxSelect>>", self.on_select)

        frame = tk.Frame(self, bg="#222831")
        frame.pack(pady=10)

        self.btn_prev = ttk.Button(frame, text="⏮ Précédent", command=self.prev_music)
        self.btn_prev.grid(row=0, column=0, padx=5)

        self.btn_play = ttk.Button(frame, text="▶️ Lecture", command=self.play_music)
        self.btn_play.grid(row=0, column=1, padx=5)

        self.btn_pause = ttk.Button(frame, text="⏸ Pause", command=self.pause_music)
        self.btn_pause.grid(row=0, column=2, padx=5)

        self.btn_next = ttk.Button(frame, text="⏭ Suivant", command=self.next_music)
        self.btn_next.grid(row=0, column=3, padx=5)

        self.btn_stop = ttk.Button(frame, text="⏹ Stop", command=self.stop_music)
        self.btn_stop.grid(row=0, column=4, padx=5)
        
        self.btn_shuffle = ttk.Button(frame, text="🔀 Aléatoire", command=self.shuffle_music)
        self.btn_shuffle.grid(row=0, column=5, padx=5)

        self.repeat = False
        self.btn_repeat = ttk.Button(frame, text="🔁 Boucle (Off)", command=self.toggle_repeat)
        self.btn_repeat.grid(row=0, column=6, padx=5)

        self.btn_voice = ttk.Button(self, text="🎤 Commande vocale", command=self.voice_command)
        self.btn_voice.pack(pady=10)

        self.label_cmd = ttk.Label(self, text="", font=("Segoe UI", 12))
        self.label_cmd.pack(pady=5)

        self.update_current()
        
                
        # Slider de volume
        self.volume = tk.DoubleVar(value=0.5)
        pygame.mixer.music.set_volume(self.volume.get())
        volume_frame = tk.Frame(self, bg="#222831")
        volume_frame.pack(pady=5)
        ttk.Label(volume_frame, text="Volume", font=("Segoe UI", 12)).pack(side=tk.LEFT)
        self.slider_volume = ttk.Scale(volume_frame, from_=0, to=1, orient=tk.HORIZONTAL, variable=self.volume, command=self.change_volume, length=150)
        self.slider_volume.pack(side=tk.LEFT, padx=10)

        self.update_current()
        
    def change_volume(self, event=None):
         pygame.mixer.music.set_volume(self.volume.get())
        
    def process_voice_command(self, commande):
        global index_actuel, en_pause
        if "plus fort" in commande or "augmente le volume" in commande:
            new_vol = min(self.volume.get() + 0.1, 1.0)
            self.volume.set(new_vol)
            pygame.mixer.music.set_volume(new_vol)
            self.label_cmd.config(text=f"Volume : {int(new_vol*100)}%")
        elif "moins fort" in commande or "baisse le volume" in commande:
            new_vol = max(self.volume.get() - 0.1, 0.0)
            self.volume.set(new_vol)
            pygame.mixer.music.set_volume(new_vol)
            self.label_cmd.config(text=f"Volume : {int(new_vol*100)}%")
    
    def update_current(self):
        if pygame.mixer.music.get_busy():
            self.label_current.config(text=f"Lecture : {musics[index_actuel]}")
        else:
            self.label_current.config(text="Lecture : Aucun")

    def on_select(self, event):
        selection = self.listbox.curselection()
        if selection:
            jouer_musique(selection[0])
            self.update_current()

    def play_music(self):
        selection = self.listbox.curselection()
        if selection:
            jouer_musique(selection[0])
        else:
            jouer_musique(index_actuel)
        self.update_current()

    def pause_music(self):
        if pygame.mixer.music.get_busy():
            pygame.mixer.music.pause()
            self.label_current.config(text="En pause")
        else:
            self.label_current.config(text="Rien à mettre en pause")

    def next_music(self):
        global index_actuel
        index_actuel = (index_actuel + 1) % len(musics)
        jouer_musique(index_actuel)
        self.listbox.selection_clear(0, tk.END)
        self.listbox.selection_set(index_actuel)
        self.update_current()

    def prev_music(self):
        global index_actuel
        index_actuel = (index_actuel - 1) % len(musics)
        jouer_musique(index_actuel)
        self.listbox.selection_clear(0, tk.END)
        self.listbox.selection_set(index_actuel)
        self.update_current()

    def stop_music(self):
        pygame.mixer.music.stop()
        self.label_current.config(text="Lecture : Aucun")

    def voice_command(self):
        self.label_cmd.config(text="J'écoute...")
        self.update()
        commande = ecouter()
        if commande:
            self.label_cmd.config(text=f"Commande : {commande}")
            self.process_voice_command(commande)
        else:
            self.label_cmd.config(text="Commande non reconnue.")

    def process_voice_command(self, commande):
        global index_actuel, en_pause
        if "pause" in commande and pygame.mixer.music.get_busy():
            pygame.mixer.music.pause()
            en_pause = True
            self.label_current.config(text="En pause")
        elif "reprends" in commande or "reprise" in commande:
            if en_pause:
                pygame.mixer.music.unpause()
                en_pause = False
                self.label_current.config(text=f"Lecture : {musics[index_actuel]}")
            else:
                self.label_current.config(text="La musique n'est pas en pause.")
        elif "stop" in commande:
            pygame.mixer.music.stop()
            self.label_current.config(text="Lecture : Aucun")
        elif "suivant" in commande or "musique suivante" in commande:
            index_actuel = (index_actuel + 1) % len(musics)
            jouer_musique(index_actuel)
            self.listbox.selection_clear(0, tk.END)
            self.listbox.selection_set(index_actuel)
            self.update_current()
        elif "retour" in commande or "reviens en arrière" in commande:
            index_actuel = (index_actuel - 1) % len(musics)
            jouer_musique(index_actuel)
            self.listbox.selection_clear(0, tk.END)
            self.listbox.selection_set(index_actuel)
            self.update_current()
        else:
            match = re.search(r"musique(?: numéro)? (\d+)", commande)
            if match:
                num = int(match.group(1))
                if 1 <= num <= len(musics):
                    jouer_musique(num - 1)
                    self.listbox.selection_clear(0, tk.END)
                    self.listbox.selection_set(num - 1)
                    self.update_current()
                else:
                    self.label_cmd.config(text="Numéro de musique invalide.")
            else:
                self.label_cmd.config(text="Commande non reconnue.")
    def update_time(self):
        if pygame.mixer.music.get_busy():
            pos = pygame.mixer.music.get_pos() // 1000
            try:
                fichier = os.path.join(MUSIC_FOLDER, musics[index_actuel])
                audio = MP3(fichier)
                total = int(audio.info.length)
            except Exception:
                total = 0
            self.label_time.config(text=f"{pos//60:02d}:{pos%60:02d} / {total//60:02d}:{total%60:02d}")
            # Barre de progression
            if total > 0:
                progress = (pos / total) * 100
                self.progress_var.set(progress)
            else:
                self.progress_var.set(0)
        else:
            self.label_time.config(text="00:00 / 00:00")
            self.progress_var.set(0)
            # Relancer la musique si boucle activée
            if getattr(self, 'repeat', False) and len(musics) > 0:
                jouer_musique(index_actuel)
        self.after(1000, self.update_time)
        
    def shuffle_music(self):
        import random
        global index_actuel
        index_actuel = random.randint(0, len(musics) - 1)
        jouer_musique(index_actuel)
        self.listbox.selection_clear(0, tk.END)
        self.listbox.selection_set(index_actuel)
        self.update_current()

    def toggle_repeat(self):
        self.repeat = not self.repeat
        if self.repeat:
            self.btn_repeat.config(text="🔁 Boucle (On)")
        else:
            self.btn_repeat.config(text="🔁 Boucle (Off)")
    
    def show_lyrics(self):
      titre = musics[index_actuel].replace(".mp3", "")
      afficher_lyrics(titre)


# --- Lancement de l'interface ---
if __name__ == "__main__":
    app = MusicAssistantApp()
    app.mainloop()