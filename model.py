# model.py

import datetime
import qrcode
import os

class Produit:
    compteur = 0  # Compteur partagé pour garantir l'unicité

    def __init__(self, nom):
        self.nom = nom
        self.id = self.unique_id_generator()
        self.qr_code = self.generate_qr_code()
        self.entrepot = None
        self.casier = None

    def __repr__(self):
        return f"Produit(id={self.id}, nom={self.nom})"
    
    def unique_id_generator(self):
        Produit.compteur += 1  # Incrémenter le compteur de classe
        date_heure = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        id_produit = f"{date_heure}_{Produit.compteur}"
        return id_produit
    
    def generate_qr_code(self):
        # Générer le QR code avec l'ID du produit comme contenu
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=4,
        )
        qr.add_data(f"ID: {self.id} - Nom: {self.nom}")
        qr.make(fit=True)

        # Générer l'image du QR code
        img = qr.make_image(fill='black', back_color='white')

        # Sauvegarder l'image QR code dans un fichier PNG
        qr_code_path = f"qr_{self.id}.png"
        img.save(qr_code_path)
        return qr_code_path  # Retourner le chemin du fichier

    def set_entrepot(self, entrepot):
        self.entrepot = entrepot

    def set_casier(self, casier):
        self.casier = casier
