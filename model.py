# model.py

import datetime
import qrcode
import os

class Produit:
    def __init__(self, nom, client, description, entrepot, emplacement, id_produit=None):
        self.nom = nom
        self.client = client
        self.description = description
        self.id = id_produit  # ID unique généré par Firebase
        self.qr_code = self.generate_qr_code()
        self.entrepot = entrepot
        self.emplacement = emplacement
        self.date = datetime.datetime.now()

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

        return img

    def set_entrepot(self, nouvel_entrepot):
        self.entrepot = nouvel_entrepot

    def set_emplacement(self, nouvel_emplacement):
        self.emplacement = nouvel_emplacement

    def get_id(self):
        return self.id
    
    def get_date(self):
        return self.date
    
    def get_description(self):
        return self.description
    
    def update_date(self):
        self.date = datetime.datetime.now()

class Entrepot:
    def __init__(self, nom, commune, nombre_etages, emplacements_par_etage):
        self.nom = nom
        self.commune = commune
        self.nombre_etages = nombre_etages
        self.emplacements_par_etage = emplacements_par_etage
        self.emplacements = self.creer_emplacements()

    def creer_emplacements(self):
        alphabet = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
        emplacements = {}
        for etage in range(self.nombre_etages):
            for num in range(self.emplacements_par_etage):
                nom_emplacement = f"{alphabet[etage]}{num + 1}"
                emplacements[nom_emplacement] = Emplacement(nom_emplacement,self.nom)
        return emplacements

    def get_emplacement(self, nom_emplacement):
        return self.emplacements.get(nom_emplacement)

    def lister_emplacements(self):
        return list(self.emplacements.values())  # Retourner une liste de tous les objets Emplacement



class Emplacement:
    def __init__(self, nom, entrepot, produit=None):
        self.nom = nom  # Nom de l'emplacement (ex: "A1")
        self.entrepot = entrepot
        self.produit = produit  # Produit assigné à l'emplacement, None s'il est vide

    def est_vide(self):
        return self.produit is None

    def assigner_produit(self, produit):
        self.produit = produit

    def liberer(self):
        self.produit = None

class Client:
    def __init__(self, nom):
        self.nom = nom
        self.historique = []

    def ajouter_au_historique(self, produit):
        self.historique.append(produit)

    def get_historique(self):
        return self.historique
