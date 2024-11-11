import sounddevice as sd
from scipy.io.wavfile import write
import numpy as np
import threading
import keyboard
from datetime import datetime
import os
import queue

class EnregistreurAudio:
    def __init__(self):
        self.frequence = 44100  # Fréquence d'échantillonnage (44.1 kHz)
        self.channels = 2
        self.enregistrement_en_cours = False
        self.frames = []
        self.stream_entree = None
        self.stream_sortie = None
        self.queue_audio = queue.Queue()
        self.block_size = 1024  # Taille du buffer audio

    def callback_entree(self, indata, frames, time, status):
        """Callback pour la capture audio"""
        if status:
            print(status)
        if self.enregistrement_en_cours:
            self.frames.append(indata.copy())
            self.queue_audio.put(indata.copy())

    def callback_sortie(self, outdata, frames, time, status):
        """Callback pour la lecture audio en temps réel"""
        if status:
            print(status)
        try:
            outdata[:] = self.queue_audio.get_nowait()
        except queue.Empty:
            outdata.fill(0)

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
        try:
            # Configuration des streams audio
            with sd.InputStream(callback=self.callback_entree, 
                              channels=self.channels,
                              samplerate=self.frequence,
                              blocksize=self.block_size), \
                 sd.OutputStream(callback=self.callback_sortie,
                               channels=self.channels,
                               samplerate=self.frequence,
                               blocksize=self.block_size):
                
                print("=== Enregistreur Audio avec Écoute en Direct ===")
                print("Appuyez sur 's' pour démarrer l'enregistrement")
                print("Appuyez sur 'q' pour arrêter l'enregistrement")
                print("Appuyez sur 'x' pour quitter le programme")
                print("Appuyez sur 'm' pour activer/désactiver le micro")
                
                micro_actif = True  # État initial du micro
                
                while True:
                    if keyboard.is_pressed('s') and not self.enregistrement_en_cours:
                        self.demarrer_enregistrement()
                        
                    elif keyboard.is_pressed('q') and self.enregistrement_en_cours:
                        self.arreter_enregistrement()
                        
                    elif keyboard.is_pressed('m'):
                        micro_actif = not micro_actif
                        if micro_actif:
                            print("\nMicro activé")
                        else:
                            print("\nMicro désactivé")
                            # Vider la queue audio quand le micro est désactivé
                            while not self.queue_audio.empty():
                                try:
                                    self.queue_audio.get_nowait()
                                except queue.Empty:
                                    break
                        # Petit délai pour éviter les rebonds
                        sd.sleep(200)
                        
                    elif keyboard.is_pressed('x'):
                        if self.enregistrement_en_cours:
                            self.arreter_enregistrement()
                        print("\nFin du programme")
                        break

                    # Si le micro est désactivé, vider la queue
                    if not micro_actif:
                        while not self.queue_audio.empty():
                            try:
                                self.queue_audio.get_nowait()
                            except queue.Empty:
                                break

        except Exception as e:
            print(f"Erreur: {str(e)}")
        finally:
            if self.enregistrement_en_cours:
                self.arreter_enregistrement()

def main():
    # Vérifier si le dossier 'enregistrements' existe, sinon le créer
    if not os.path.exists('enregistrements'):
        os.makedirs('enregistrements')
        
    enregistreur = EnregistreurAudio()
    enregistreur.executer()

if __name__ == "__main__":
    main()