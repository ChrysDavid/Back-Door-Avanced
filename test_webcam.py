import cv2
import os
from datetime import datetime
import keyboard
import time

class ControleurCamera:
    def __init__(self):
        self.camera = None
        self.sortie_video = None
        self.enregistrement_en_cours = False
        
    def initialiser_camera(self):
        """Initialise la caméra"""
        self.camera = cv2.VideoCapture(0)
        if not self.camera.isOpened():
            raise Exception("Impossible d'accéder à la caméra.")
        
        # Créer le dossier 'captures' s'il n'existe pas
        if not os.path.exists('captures'):
            os.makedirs('captures')
            
    def capturer_image(self):
        """Capture une image unique"""
        try:
            self.initialiser_camera()
            
            # Afficher l'aperçu
            print("Appuyez sur 'espace' pour prendre la photo ou 'q' pour annuler")
            while True:
                ret, frame = self.camera.read()
                if not ret:
                    raise Exception("Erreur lors de la capture du flux vidéo")
                
                # Afficher l'aperçu
                cv2.imshow('Aperçu (Espace: Capturer, Q: Quitter)', frame)
                
                # Gestion des touches
                key = cv2.waitKey(1)
                if keyboard.is_pressed('space'):  # Capture quand espace est pressé
                    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                    nom_fichier = f"captures/photo_{timestamp}.jpg"
                    cv2.imwrite(nom_fichier, frame)
                    print(f"\nPhoto sauvegardée: {nom_fichier}")
                    break
                elif keyboard.is_pressed('q'):  # Quitter sans capturer
                    print("\nCapture annulée")
                    break
                    
        finally:
            if self.camera is not None:
                self.camera.release()
            cv2.destroyAllWindows()

    def demarrer_enregistrement(self):
        """Démarre l'enregistrement vidéo"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        nom_fichier = f"captures/video_{timestamp}.avi"
        
        largeur = int(self.camera.get(cv2.CAP_PROP_FRAME_WIDTH))
        hauteur = int(self.camera.get(cv2.CAP_PROP_FRAME_HEIGHT))
        codec = cv2.VideoWriter_fourcc(*"XVID")
        fps = 20.0
        
        self.sortie_video = cv2.VideoWriter(nom_fichier, codec, fps, (largeur, hauteur))
        self.enregistrement_en_cours = True
        print("\nEnregistrement démarré... Appuyez sur 'q' pour arrêter")
        
    def arreter_enregistrement(self):
        """Arrête l'enregistrement vidéo"""
        self.enregistrement_en_cours = False
        if self.sortie_video is not None:
            self.sortie_video.release()
        print("\nEnregistrement terminé")
            
    def enregistrer_video(self):
        """Gère l'enregistrement vidéo avec contrôle par touches"""
        try:
            self.initialiser_camera()
            
            print("Appuyez sur 's' pour démarrer l'enregistrement")
            print("Appuyez sur 'q' pour arrêter l'enregistrement")
            print("Appuyez sur 'x' pour quitter")
            
            while True:
                ret, frame = self.camera.read()
                if not ret:
                    break
                
                # Afficher le flux vidéo
                cv2.imshow('Enregistrement Vidéo (S: Démarrer, Q: Arrêter, X: Quitter)', frame)
                
                # Si enregistrement en cours, sauvegarder la frame
                if self.enregistrement_en_cours:
                    self.sortie_video.write(frame)
                
                # Gestion des touches
                if keyboard.is_pressed('s') and not self.enregistrement_en_cours:
                    self.demarrer_enregistrement()
                    time.sleep(0.3)  # Éviter les doubles appuis
                elif keyboard.is_pressed('q') and self.enregistrement_en_cours:
                    self.arreter_enregistrement()
                    time.sleep(0.3)
                elif keyboard.is_pressed('x'):
                    if self.enregistrement_en_cours:
                        self.arreter_enregistrement()
                    break
                
                if cv2.waitKey(1) & 0xFF == ord('x'):
                    break
                    
        finally:
            if self.camera is not None:
                self.camera.release()
            if self.sortie_video is not None:
                self.sortie_video.release()
            cv2.destroyAllWindows()

def menu_principal():
    """Affiche le menu principal"""
    controleur = ControleurCamera()
    
    while True:
        print("\n=== Menu Principal ===")
        print("1. Prendre une photo")
        print("2. Enregistrer une vidéo")
        print("3. Quitter")
        
        choix = input("\nVotre choix (1-3): ")
        
        if choix == "1":
            controleur.capturer_image()
        elif choix == "2":
            controleur.enregistrer_video()
        elif choix == "3":
            print("Au revoir!")
            break
        else:
            print("Choix invalide. Veuillez réessayer.")

if __name__ == "__main__":
    menu_principal()