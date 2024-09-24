# Controller.py

from model import Produit, Entrepot, Client, Emplacement  # Assurez-vous que toutes les classes sont importées
from firebase_config import db

class Controller:
    def __init__(self):
        self.entrepots = {}
        self.clients = {}
        self.produits = {}
        self.compteur = 0
        self.initialiser_compteur()
        self.recuperer_entrepots_firebase()
        self.recuperer_clients_firebase()
        self.recuperer_produits_firebase()

    def initialiser_compteur(self):
        compteur_ref = db.reference('compteur')
        compteur_data = compteur_ref.get()
        if compteur_data is None:
            compteur_ref.set(0)
            self.compteur = 0
        else:
            self.compteur = compteur_data

    def incrementer_compteur(self):
        compteur_ref = db.reference('compteur')
        self.compteur += 1
        compteur_ref.set(self.compteur)

    def recuperer_entrepots_firebase(self):
        entrepots_ref = db.reference('entrepots')
        entrepots_data = entrepots_ref.get()
        if entrepots_data:
            for nom, data in entrepots_data.items():
                self.entrepots[nom] = Entrepot(
                    nom, data['commune'], data['nombre_etages'], data['emplacements_par_etage']
                )

    def recuperer_clients_firebase(self):
        clients_ref = db.reference('clients')
        clients_data = clients_ref.get()
        if clients_data:
            for nom, data in clients_data.items():
                self.clients[nom] = Client(nom)

    def recuperer_produits_firebase(self):
        produits_ref = db.reference('produits')
        produits_data = produits_ref.get()
        if produits_data:
            for produit_id, data in produits_data.items():
                produit = Produit(
                    data['nom'], data['client_nom'], data['description'],
                    data['entrepot_nom'], data['emplacement']
                )
                self.produits[produit_id] = produit
                # Assigner le produit à son emplacement dans l'entrepôt
                emplacement = self.entrepots[data['entrepot_nom']].get_emplacement(data['emplacement'])
                if emplacement:
                    emplacement.assigner_produit(produit)

    def ajouter_entrepot(self, nom, commune, nombre_etages, emplacements_par_etage):
        if nom not in self.entrepots:
            entrepot = Entrepot(nom, commune, nombre_etages, emplacements_par_etage)
            self.entrepots[nom] = entrepot
            # Ajouter à Firebase
            db.reference('entrepots').child(nom).set({
                'commune': commune,
                'nombre_etages': nombre_etages,
                'emplacements_par_etage': emplacements_par_etage
            })
            return True
        return False

    def ajouter_client(self, nom):
        if nom not in self.clients:
            client = Client(nom)
            self.clients[nom] = client
            # Ajouter à Firebase
            db.reference('clients').child(nom).set({
                'nom': nom
            })
            return True
        return False

    def ajouter_produit(self, nom, client_nom, description, entrepot_nom, emplacement_nom):
        if client_nom in self.clients and entrepot_nom in self.entrepots:
            # Incrémenter le compteur pour obtenir un nouvel ID unique
            self.incrementer_compteur()
            id_produit = f"prod-{self.compteur}"  # Créer un ID unique pour le produit

            produit = Produit(nom, client_nom, description, entrepot_nom, emplacement_nom)
            produit.id = id_produit  # Assigner l'ID unique au produit

            produit_ref = db.reference('produits').child(id_produit)
            produit_ref.set({
                'nom': nom,
                'client_nom': client_nom,
                'description': description,
                'entrepot_nom': entrepot_nom,
                'emplacement': emplacement_nom
            })

            # Ajouter le produit à la liste en mémoire
            self.produits[id_produit] = produit
            # Assigner le produit à l'emplacement
            emplacement = self.entrepots[entrepot_nom].get_emplacement(emplacement_nom)
            if emplacement:
                emplacement.assigner_produit(produit)
            return produit
        return None

    def est_emplacement_vide(self, entrepot_nom, emplacement_nom):
        emplacement = self.entrepots[entrepot_nom].get_emplacement(emplacement_nom)
        if emplacement:
            return emplacement.est_vide()
        return False

    def deplacer_produit(self, ancien_entrepot, ancien_emplacement_obj, nouvel_entrepot, nouvel_emplacement_obj):
        # Assurer que les objets Emplacement sont valides
        if not ancien_emplacement_obj or not nouvel_emplacement_obj:
            print("Erreur : Les objets d'emplacement ne sont pas valides.")
            return False

        # Vérifier si l'emplacement d'origine contient bien un produit
        if ancien_emplacement_obj.est_vide():
            print(f"Erreur : L'emplacement {ancien_emplacement_obj.nom} dans l'entrepôt {ancien_entrepot} est vide.")
            return False

        produit = ancien_emplacement_obj.produit

        # Vérifier si le nouvel emplacement est vide
        if not nouvel_emplacement_obj.est_vide():
            print(f"Erreur : L'emplacement {nouvel_emplacement_obj.nom} dans l'entrepôt {nouvel_entrepot} est déjà occupé.")
            return False

        # Déplacement du produit
        nouvel_emplacement_obj.assigner_produit(produit)  # Assigner le produit au nouvel emplacement
        ancien_emplacement_obj.liberer()  # Libérer l'ancien emplacement
        print(f"Produit {produit.nom} libéré de l'emplacement {ancien_emplacement_obj.nom} ({ancien_entrepot})")

        # Mise à jour de l'emplacement du produit
        produit.entrepot = nouvel_entrepot  # Mettre à jour l'entrepôt du produit
        produit.emplacement = nouvel_emplacement_obj.nom  # Mettre à jour l'emplacement du produit
        print(f"Produit {produit.nom} mis à jour avec le nouvel emplacement {produit.emplacement} dans l'entrepôt {produit.entrepot}")

        # Mettre à jour Firebase
        try:
            produit_id = [key for key, value in self.produits.items() if value.nom == produit.nom][0]
            db.reference('produits').child(produit_id).update({
                'entrepot_nom': nouvel_entrepot,
                'emplacement': nouvel_emplacement_obj.nom  # Utiliser le nom de l'emplacement pour la mise à jour dans Firebase
            })
        except IndexError:
            print("Erreur : Produit non trouvé dans le dictionnaire self.produits.")
            return False

        print(f"Succès : Produit {produit.nom} déplacé de {ancien_emplacement_obj.nom} ({ancien_entrepot}) vers {nouvel_emplacement_obj.nom} ({nouvel_entrepot}).")
        return True


    def get_entrepots(self):
        return self.entrepots

    def get_clients(self):
        return self.clients

    def get_emplacements(self, entrepot_nom):
        if entrepot_nom in self.entrepots:
            return {emplacement.nom: emplacement.produit.nom if emplacement.produit else None
                    for emplacement in self.entrepots[entrepot_nom].lister_emplacements()}
        return {}
