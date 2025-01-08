from Model.model import Produit, Entrepot, Client, Emplacement  # Importer les classes du modèle
from Model.firebase_config import db  # Importer la configuration de Firebase
import datetime

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

    def ajouter_client(self, nom, adresse, nom_societe):
        if nom not in self.clients:
            client = Client(nom, adresse, nom_societe)  # Passer l'adresse et le nom de la société
            self.clients[nom] = client
            # Ajouter à Firebase
            db.reference('clients').child(nom).set({
                'nom': nom,
                'adresse': adresse,
                'nom_societe': nom_societe
            })
            return True
        return False

    def editer_client(self, nom_client_initial, nouveau_nom, nouvelle_adresse, nouveau_nom_societe):
        """
        Met à jour les informations d'un client.
        """
        if nom_client_initial in self.clients:
            client = self.clients[nom_client_initial]

            # Mettre à jour les attributs du client
            client.nom = nouveau_nom
            client.adresse = nouvelle_adresse
            client.nom_societe = nouveau_nom_societe

            # Mettre à jour Firebase ou la base de données si nécessaire
            db.reference('clients').child(nom_client_initial).update({
                'nom': nouveau_nom,
                'adresse': nouvelle_adresse,
                'nom_societe': nouveau_nom_societe
            })

            # Si le nom du client a changé, mettre à jour le dictionnaire des clients
            if nouveau_nom != nom_client_initial:
                del self.clients[nom_client_initial]
                self.clients[nouveau_nom] = client

            return True

        return False


    def ajouter_produit(self, nom, client_nom, description, entrepot_nom, emplacement_nom):
        if client_nom in self.clients and entrepot_nom in self.entrepots:
            # Incrémenter le compteur pour obtenir un nouvel ID unique
            self.incrementer_compteur()
            id_produit = f"prod-{self.compteur}"  # Créer un ID unique pour le produit

            # Créer un produit avec la date actuelle
            produit = Produit(nom, client_nom, description, entrepot_nom, emplacement_nom)
            produit.id = id_produit  # Assigner l'ID unique au produit

            # Enregistrer le produit dans Firebase, incluant la date d'entrée
            produit_ref = db.reference('produits').child(id_produit)
            produit_ref.set({
                'nom': nom,
                'client_nom': client_nom,
                'description': description,
                'entrepot_nom': entrepot_nom,
                'emplacement': emplacement_nom,
                'date_entree': produit.date_entree.strftime('%Y-%m-%d')  # Format de la date
            })

            # Ajouter le produit à la liste en mémoire
            self.produits[id_produit] = produit

            # Assigner le produit à l'emplacement
            emplacement = self.entrepots[entrepot_nom].get_emplacement(emplacement_nom)
            if emplacement:
                emplacement.assigner_produit(produit)
            
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

    def editer_produit(self, produit_id, nom, description):
        """
        Met à jour un produit dans la base de données et en mémoire.
        """
        if produit_id in self.produits:
            produit = self.produits[produit_id]
            produit.nom = nom
            produit.description = description

            # Mettre à jour Firebase
            produit_ref = db.reference('produits').child(produit_id)
            produit_ref.update({
                'nom': nom,
                'description': description
            })

            return True
        return False
    
    def editer_entrepot(self, nom_actuel, nouveau_nom, commune, nombre_etages, emplacements_par_etage):
        if nom_actuel in self.entrepots:
            # Récupérer l'entrepôt actuel
            entrepot = self.entrepots.pop(nom_actuel)

            # Supprimer l'ancien enregistrement dans Firebase
            db.reference('entrepots').child(nom_actuel).delete()

            # Mettre à jour les informations de l'entrepôt
            entrepot.nom = nouveau_nom
            entrepot.commune = commune
            entrepot.nombre_etages = nombre_etages
            entrepot.emplacements_par_etage = emplacements_par_etage

            # Ajouter le nouvel entrepôt dans Firebase
            db.reference('entrepots').child(nouveau_nom).set({
                'commune': commune,
                'nombre_etages': nombre_etages,
                'emplacements_par_etage': emplacements_par_etage
            })

            # Mettre à jour le dictionnaire des entrepôts en mémoire
            self.entrepots[nouveau_nom] = entrepot

            # ✅ Mettre à jour les produits liés à cet entrepôt
            for produit_id, produit in self.produits.items():
                if produit.entrepot == nom_actuel:
                    # Mettre à jour l'attribut dans l'objet produit
                    produit.entrepot = nouveau_nom

                    # Mettre à jour Firebase
                    db.reference('produits').child(produit_id).update({
                        'entrepot_nom': nouveau_nom
                    })

            return True
        return False


    def supprimer_produit(self, id_produit):
        if id_produit in self.produits:
            produit = self.produits[id_produit]
            
            # Récupérer la date d'entrée depuis Firebase
            date_entree = self.recuperer_date_entree(id_produit)
            if isinstance(date_entree, str):
                # Vérifier si la date récupérée est valide
                try:
                    date_entree = datetime.datetime.strptime(date_entree, '%Y-%m-%d')
                except ValueError:
                    print("Erreur : La date d'entrée récupérée est invalide.")
                    date_entree = None

            # Ajouter la date de départ
            date_depart = datetime.datetime.now().strftime('%Y-%m-%d')
            
            # Archiver le produit dans 'produits_supprimes'
            produit_archive = {
                'nom': produit.nom,
                'client_nom': produit.client,
                'description': produit.description,
                'entrepot_nom': produit.entrepot,
                'emplacement': produit.emplacement,
                'date_entree': date_entree.strftime('%Y-%m-%d') if date_entree else 'Date inconnue',
                'date_depart': date_depart,  # Ajouter la date de départ
                'numero_facture':  f"{datetime.datetime.now().strftime('%Y%m%d')}{produit.id.replace('prod-', '')}"
            }
            
            # Enregistrer dans la collection d'archives
            archive_ref = db.reference('produits_supprimes').child(id_produit)
            archive_ref.set(produit_archive)
            
            # Supprimer le produit de la collection principale
            produit_ref = db.reference('produits').child(id_produit)
            produit_ref.delete()
            
            # Retirer de la liste en mémoire
            del self.produits[id_produit]
            
            # Libérer l'emplacement dans l'entrepôt
            emplacement = self.entrepots[produit.entrepot].get_emplacement(produit.emplacement)
            if emplacement:
                emplacement.liberer()

            print(f"Produit {produit.nom} supprimé et archivé avec succès.")
        else:
            print("Produit non trouvé.")


    def recuperer_date_entree(self, produit_id):
        """
        Récupère la date d'entrée du produit depuis Firebase.
        """
        produit_data = db.reference(f"produits/{produit_id}").get()
        if produit_data:
            # Retourner la date d'entrée stockée dans Firebase
            return produit_data.get('date_entree', 'Date non disponible')
        return 'Date non disponible'

    def get_entrepots(self):
        return self.entrepots

    def get_clients(self):
        return self.clients

    def get_emplacements(self, entrepot_nom):
        if entrepot_nom in self.entrepots:
            return {emplacement.nom: emplacement.produit.nom if emplacement.produit else None
                    for emplacement in self.entrepots[entrepot_nom].lister_emplacements()}
        return {}
    
    def recuperer_data_client(self, client_nom):
        """
        Récupère les informations d'un client depuis Firebase.
        """
        client_data = db.reference(f"clients/{client_nom}").get()
        if client_data:
            return {
                "nom": client_data.get("nom", "Nom inconnu"),
                "adresse": client_data.get("adresse", "Adresse non spécifiée"),
                "nom_societe": client_data.get("nom_societe", "Société non spécifiée")
            }
        return {
            "nom": "Nom inconnu",
            "adresse": "Adresse non spécifiée",
            "nom_societe": "Société non spécifiée"
        }


    def get_historique_produits_supprimes(self):
        """
        Récupère l'historique des produits supprimés depuis Firebase.
        """
        produits_supprimes = db.reference('produits_supprimes').get()
        if not produits_supprimes:
            return []

        # Structurer les données correctement
        historique = []
        for produit_id, produit_data in produits_supprimes.items():
            historique.append({
                'id': produit_id,
                'nom': produit_data.get('nom', 'Nom inconnu'),
                'client_nom': produit_data.get('client_nom', 'Client inconnu'),
                'description': produit_data.get('description', 'Description non spécifiée'),
                'entrepot_nom': produit_data.get('entrepot_nom', 'Entrepôt inconnu'),
                'emplacement': produit_data.get('emplacement', 'Emplacement inconnu'),
                'date_entree': produit_data.get('date_entree', 'Date inconnue'),
                'date_depart': produit_data.get('date_depart', 'Date inconnue'),
                'numero_facture': produit_data.get('numero_facture', 'Non disponible')
            })
        return historique
