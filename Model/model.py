# model.py

import datetime
import os

class Produit:
    def __init__(self, nom, client, description, entrepot, emplacement, id_produit=None):
        self.nom = nom
        self.client = client
        self.description = description
        self.id = id_produit  # ID unique généré par Firebase
        self.entrepot = entrepot
        self.emplacement = emplacement
        self.date_entree = None
        self.date_depart = None
        self.date_modif = None
        self.generate_date_entree()

    def generate_date_entree(self):
        self.date_entree = datetime.datetime.now()

    def set_entrepot(self, nouvel_entrepot):
        self.entrepot = nouvel_entrepot

    def set_emplacement(self, nouvel_emplacement):
        self.emplacement = nouvel_emplacement

    def get_id(self):
        return self.id
    
    def get_date_entree(self):
        return self.date_entree
    
    def get_date_depart(self):
        return datetime.datetime.now()
    
    def get_description(self):
        return self.description
    
    def update_date(self):
        self.date_modif = datetime.datetime.now()

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
        return list(self.emplacements.values())  # Retourner une liste de tous les objets Emplacemen
    
    def liste_emplacements_pleins(self):

        emplacements_plein = []
        for emplacement in self.emplacements.values():
            if not emplacement.est_vide():
                emplacements_plein.append(emplacement.produit)
        return emplacements_plein


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
    def __init__(self, nom, adresse = None, nom_societe = None):
        self.nom = nom
        self.historique = []
        self.adresse = adresse
        self.nom_societe = nom_societe

    def ajouter_au_historique(self, produit):
        self.historique.append(produit)

    def get_historique(self):
        return self.historique
