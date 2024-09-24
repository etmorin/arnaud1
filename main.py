# main.py

# Importer la configuration Firebase et les modules MVC
from firebase_config import db
from controller import Controller
from view import View
import tkinter as tk

# Initialiser l'application en récupérant les données depuis Firebase
def main():
    # Créer la fenêtre principale de l'application Tkinter
    root = tk.Tk()
    
    # Créer le contrôleur pour gérer les données
    controller = Controller()

    # Créer la vue (interface utilisateur) en utilisant le contrôleur
    app = View(root, controller)

    # Lancer l'interface graphique Tkinter
    root.mainloop()

# Point d'entrée de l'application
if __name__ == "__main__":
    main()
