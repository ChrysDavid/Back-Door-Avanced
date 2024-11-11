import sounddevice as sd
from scipy.io.wavfile import write
import numpy as np
import keyboard
from datetime import datetime
import os

class EnregistreurAudio:
    def __init__(self):
        self.frequence = 44100  # Fréquence d'échantillonnage (44.1 kHz)
        self.channels = 2
        self.enregistrement_en_cours = False
        self.frames = []
        self.thread_enregistrement = None

    def callback(self, indata, frames, time, status):
        """Callback appelé pour chaque bloc audio capturé"""
        if status:
            print(status)
        if self.enregistrement_en_cours:
            self.frames.append(indata.copy())

    def demarrer_enregistrement(self):
        """Démarre l'enregistrement"""
        if not self.enregistrement_en_cours:
            self.frames = []
            self.enregistrement_en_cours = True
            print("\nEnregistrement démarré... (Appuyez sur 'q' pour arrêter)")

    def arreter_enregistrement(self):
        """Arrête l'enregistrement et sauvegarde le fichier"""
        if self.enregistrement_en_cours:
            self.enregistrement_en_cours = False
            
            if len(self.frames) > 0:
                # Créer le nom du fichier avec la date et l'heure
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                nom_fichier = f"enregistrement_{timestamp}.wav"
                
                # Créer le dossier 'enregistrements' s'il n'existe pas
                if not os.path.exists('enregistrements'):
                    os.makedirs('enregistrements')
                
                chemin_fichier = os.path.join('enregistrements', nom_fichier)
                
                # Convertir les frames en array numpy
                audio_data = np.concatenate(self.frames, axis=0)
                
                # Sauvegarder le fichier
                write(chemin_fichier, self.frequence, audio_data)
                print(f"\nEnregistrement sauvegardé: {chemin_fichier}")
            else:
                print("\nAucun audio enregistré")

    def executer(self):
        """Fonction principale qui gère l'enregistrement"""
        print("Appuyez sur 's' pour démarrer l'enregistrement")
        print("Appuyez sur 'q' pour arrêter l'enregistrement")
        print("Appuyez sur 'x' pour quitter le programme")

        try:
            with sd.InputStream(callback=self.callback, 
                              channels=self.channels,
                              samplerate=self.frequence):
                
                while True:
                    if keyboard.is_pressed('s') and not self.enregistrement_en_cours:
                        self.demarrer_enregistrement()
                    elif keyboard.is_pressed('q') and self.enregistrement_en_cours:
                        self.arreter_enregistrement()
                    elif keyboard.is_pressed('x'):
                        if self.enregistrement_en_cours:
                            self.arreter_enregistrement()
                        print("\nFin du programme")
                        break

        except Exception as e:
            print(f"Erreur: {str(e)}")
        finally:
            if self.enregistrement_en_cours:
                self.arreter_enregistrement()

if __name__ == "__main__":
    enregistreur = EnregistreurAudio()
    enregistreur.executer()