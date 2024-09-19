# controller.py

import csv
from model import Produit
from view import QRCodeView

class QRCodeController:
    def __init__(self):
        self.produits = []
        self.fichier_csv = 'produits.csv'

    def ajouter_produit(self, nom_produit):
        # Créer un nouveau produit
        produit = Produit(nom_produit)
        self.produits.append(produit)

        # Sauvegarder le produit dans un fichier CSV
        self.sauvegarder_produit_csv(produit)

        # Afficher les informations du produit via la vue
        QRCodeView.imprimer_qr_code(produit)

    def ajouter_produit_interactif(self):
        # Demander le nom du produit
        nom_produit = input("Entrez le nom du produit : ")
        
        # Ajouter le produit
        self.ajouter_produit(nom_produit)

    def sauvegarder_produit_csv(self, produit):
        # Sauvegarder un produit dans le fichier CSV
        with open(self.fichier_csv, mode='a', newline='') as fichier:
            writer = csv.writer(fichier)
            writer.writerow([produit.id, produit.nom, produit.qr_code])
