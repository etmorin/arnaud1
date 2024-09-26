from model import Produit, Entrepot, Client, Emplacement  # Importer les classes du modèle
from firebase_config import db  # Importer la configuration de Firebase

class Controller:
    def __init__(self):
        self.entrepots = {}
        self.clients = {}
        self.produits = {}
        self.compteur = 0
        self.initialiser_compteur()
        self.recuperer_donnees('entrepots', Entrepot, self.entrepots)
        self.recuperer_donnees('clients', Client, self.clients)
        self.recuperer_donnees('produits', Produit, self.produits, additional_processing=self.assigner_produit_emplacement)

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

    def recuperer_donnees(self, reference, classe, stockage, additional_processing=None):
        ref = db.reference(reference)
        data = ref.get()
        if data:
            for key, valeur in data.items():
                if classe == Entrepot:
                    instance = classe(
                        nom=key,
                        commune=valeur['commune'],
                        nombre_etages=valeur['nombre_etages'],
                        emplacements_par_etage=valeur['emplacements_par_etage']
                    )
                elif classe == Client:
                    instance = classe(nom=key)
                elif classe == Produit:
                    instance = classe(
                        nom=valeur['nom'], 
                        client=valeur['client_nom'], 
                        description=valeur['description'],
                        entrepot=valeur['entrepot_nom'], 
                        emplacement=valeur['emplacement'],
                        id_produit=key
                    )
                else:
                    instance = classe(**valeur)

                stockage[key] = instance

                if additional_processing:
                    additional_processing(instance, valeur)

    def assigner_produit_emplacement(self, produit, valeur):
        """
        Assigne le produit à son emplacement dans l'entrepôt.
        """
        entrepot_nom = valeur['entrepot_nom']
        emplacement_nom = valeur['emplacement']
        if entrepot_nom in self.entrepots:
            emplacement = self.entrepots[entrepot_nom].get_emplacement(emplacement_nom)
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
        """
        Ajoute un produit à un emplacement spécifique dans un entrepôt.
        """
        if client_nom in self.clients and entrepot_nom in self.entrepots:
            # Incrémenter le compteur pour obtenir un nouvel ID unique
            self.incrementer_compteur()
            id_produit = f"prod-{self.compteur}"  # Créer un ID unique pour le produit

            # Créer l'objet Produit
            produit = Produit(nom, client_nom, description, entrepot_nom, emplacement_nom)
            produit.id = id_produit  # Assigner l'ID unique au produit

            # Enregistrer le produit dans Firebase
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
                emplacement.assigner_produit(produit)  # Mettre à jour l'objet Emplacement
            else:
                print(f"Erreur : L'emplacement {emplacement_nom} n'existe pas dans l'entrepôt {entrepot_nom}.")
            return produit
        return None


    def deplacer_produit(self, ancien_entrepot, ancien_emplacement_obj, nouvel_entrepot, nouvel_emplacement_obj):
        """
        Déplace un produit d'un emplacement à un autre.
        """
        if not ancien_emplacement_obj or not nouvel_emplacement_obj:
            print("Erreur : Les objets d'emplacement ne sont pas valides.")
            return False

        produit = ancien_emplacement_obj.produit
        if produit is None:
            print(f"Erreur : L'emplacement {ancien_emplacement_obj.nom} dans l'entrepôt {ancien_entrepot} est vide.")
            return False

        if produit.entrepot != ancien_entrepot or produit.emplacement != ancien_emplacement_obj.nom:
            print(f"Erreur : Le produit {produit.nom} n'est pas actuellement à l'emplacement {ancien_emplacement_obj.nom} dans l'entrepôt {ancien_entrepot}.")
            return False

        if not nouvel_emplacement_obj.est_vide():
            print(f"Erreur : L'emplacement {nouvel_emplacement_obj.nom} dans l'entrepôt {nouvel_emplacement_obj.nom} est déjà occupé.")
            return False

        nouvel_emplacement_obj.assigner_produit(produit)
        ancien_emplacement_obj.liberer()

        produit.entrepot = nouvel_entrepot
        produit.emplacement = nouvel_emplacement_obj.nom

        try:
            produit_id = [key for key, value in self.produits.items() if value.nom == produit.nom][0]
            db.reference('produits').child(produit_id).update({
                'entrepot_nom': nouvel_entrepot,
                'emplacement': nouvel_emplacement_obj.nom
            })
        except IndexError:
            print("Erreur : Produit non trouvé dans le dictionnaire self.produits.")
            return False

        print(f"Succès : Produit {produit.nom} déplacé de {ancien_emplacement_obj.nom} ({ancien_entrepot}) vers {nouvel_emplacement_obj.nom} ({nouvel_entrepot}).")
        return True
    
    def echanger_produits(self, entrepot_source, emplacement_source, entrepot_cible, emplacement_cible):
        """
        Échange les produits entre deux emplacements.
        """
        # Vérifier que les deux emplacements contiennent des produits
        if not emplacement_source.produit or not emplacement_cible.produit:
            print("Erreur : Les deux emplacements doivent contenir des produits pour un échange.")
            return False

        # Sauvegarder les produits temporairement
        produit_temp = emplacement_source.produit

        # Échanger les produits
        emplacement_source.assigner_produit(emplacement_cible.produit)
        emplacement_cible.assigner_produit(produit_temp)

        # Mettre à jour les informations des produits
        emplacement_source.produit.entrepot = entrepot_source.nom
        emplacement_source.produit.emplacement = emplacement_source.nom
        emplacement_cible.produit.entrepot = entrepot_cible.nom
        emplacement_cible.produit.emplacement = emplacement_cible.nom

        # Mettre à jour Firebase ou la base de données ici si nécessaire
        db.reference('produits').child(emplacement_source.produit.id).update({
            'entrepot_nom': entrepot_source.nom,
            'emplacement': emplacement_source.nom
        })
        db.reference('produits').child(emplacement_cible.produit.id).update({
            'entrepot_nom': entrepot_cible.nom,
            'emplacement': emplacement_cible.nom
        })

        print(f"Échange effectué entre {emplacement_source.nom} et {emplacement_cible.nom}.")
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
