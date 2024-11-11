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

    def afficher_apercu(self, titre="Aperçu"):
        """Affiche l'aperçu de la caméra"""
        ret, frame = self.camera.read()
        if ret:
            # Ajout du texte d'état sur l'image
            text_color = (0, 255, 0)  # Vert
            if self.enregistrement_en_cours:
                cv2.putText(frame, "Enregistrement en cours", (10, 30), 
                           cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
            
            # Ajout des instructions sur l'image
            instructions = [
                "1: Photo",
                "2: Video",
                "3: Quitter",
                "ESC: Retour"
            ]
            y = 60
            for instruction in instructions:
                cv2.putText(frame, instruction, (10, y), 
                           cv2.FONT_HERSHEY_SIMPLEX, 0.6, text_color, 2)
                y += 30

            cv2.imshow(titre, frame)
            return True
        return False
            
    def capturer_image(self):
        """Capture une image unique"""
        try:
            print("\nMode Photo")
            print("Appuyez sur 'espace' pour prendre la photo")
            print("Appuyez sur 'q' pour annuler")
            
            while True:
                ret, frame = self.camera.read()
                if not ret:
                    raise Exception("Erreur lors de la capture du flux vidéo")
                
                # Ajout des instructions sur l'image
                cv2.putText(frame, "ESPACE: Capturer", (10, 30), 
                           cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
                cv2.putText(frame, "Q: Annuler", (10, 60), 
                           cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
                
                cv2.imshow('Mode Photo', frame)
                
                # Gestion des touches
                if keyboard.is_pressed('space'):  # Capture quand espace est pressé
                    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                    nom_fichier = f"captures/photo_{timestamp}.jpg"
                    cv2.imwrite(nom_fichier, frame)
                    print(f"\nPhoto sauvegardée: {nom_fichier}")
                    # Afficher "Photo capturée" pendant 2 secondes
                    start_time = time.time()
                    while time.time() - start_time < 2:
                        capture_frame = frame.copy()
                        cv2.putText(capture_frame, "Photo capturee!", (10, 90), 
                                  cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
                        cv2.imshow('Mode Photo', capture_frame)
                        cv2.waitKey(1)
                    break
                elif keyboard.is_pressed('q'):  # Quitter sans capturer
                    print("\nCapture annulée")
                    break
                
                if cv2.waitKey(1) & 0xFF == 27:  # ESC
                    break
                    
        except Exception as e:
            print(f"Erreur: {str(e)}")

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
        print("\nEnregistrement démarré...")
        
    def arreter_enregistrement(self):
        """Arrête l'enregistrement vidéo"""
        self.enregistrement_en_cours = False
        if self.sortie_video is not None:
            self.sortie_video.release()
        print("\nEnregistrement terminé")
            
    def enregistrer_video(self):
        """Gère l'enregistrement vidéo avec contrôle par touches"""
        try:
            print("\nMode Vidéo")
            print("Appuyez sur 's' pour démarrer l'enregistrement")
            print("Appuyez sur 'q' pour arrêter l'enregistrement")
            print("Appuyez sur 'x' pour quitter")
            
            while True:
                ret, frame = self.camera.read()
                if not ret:
                    break
                
                # Ajout des instructions et état sur l'image
                if self.enregistrement_en_cours:
                    cv2.putText(frame, "Enregistrement en cours", (10, 30), 
                              cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
                    cv2.putText(frame, "Q: Arreter", (10, 60), 
                              cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
                else:
                    cv2.putText(frame, "S: Demarrer", (10, 30), 
                              cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
                cv2.putText(frame, "X: Quitter", (10, 90), 
                          cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
                
                cv2.imshow('Mode Video', frame)
                
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
                
                if cv2.waitKey(1) & 0xFF == 27:  # ESC
                    if self.enregistrement_en_cours:
                        self.arreter_enregistrement()
                    break

        except Exception as e:
            print(f"Erreur: {str(e)}")

    def executer(self):
        """Exécute le programme principal avec aperçu"""
        try:
            self.initialiser_camera()
            
            while True:
                # Afficher l'aperçu avec les options
                if not self.afficher_apercu("Camera (1: Photo, 2: Video, 3: Quitter, ESC: Retour)"):
                    break
                
                key = cv2.waitKey(1) & 0xFF
                
                if keyboard.is_pressed('1'):
                    cv2.destroyAllWindows()
                    self.capturer_image()
                elif keyboard.is_pressed('2'):
                    cv2.destroyAllWindows()
                    self.enregistrer_video()
                elif keyboard.is_pressed('3') or key == 27:  # '3' ou ESC
                    break
                
        except Exception as e:
            print(f"Erreur: {str(e)}")
        finally:
            if self.camera is not None:
                self.camera.release()
            if self.sortie_video is not None:
                self.sortie_video.release()
            cv2.destroyAllWindows()

if __name__ == "__main__":
    controleur = ControleurCamera()
    controleur.executer()