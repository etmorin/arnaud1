import tkinter as tk
from tkinter import simpledialog
from Model.generate_pdf import generate_bon_entree, generate_bon_sortie
from tkinter import ttk, messagebox
from Controller.controller import Controller
from Controller.selection_context import SelectionContext
from Model.state import NeutralState, ProductSelectedState, MovingProductState, AddingProductState, NothingSelectedState

class View:
    def __init__(self, root, controller):
        self.controller = controller
        self.root = root
        self.root.title("Gestion des Entrepôts")

        self.emplacement_depart = None

        # Configurer une grille avec deux colonnes
        self.root.grid_columnconfigure(0, weight=3)
        self.root.grid_columnconfigure(1, weight=2)
        self.root.grid_rowconfigure(1, weight=1)

        # Cadre pour les boutons d'action (en haut)
        action_frame = tk.Frame(root)
        action_frame.grid(row=0, column=0, columnspan=2, padx=10, pady=10, sticky="ew")

        # Boutons d'action (Ajouter, Editer, Supprimer, etc.)
        self.btn_ajouter_entrepot = tk.Button(action_frame, text="Ajouter Entrepôt", command=self.ajouter_entrepot)
        self.btn_ajouter_entrepot.grid(row=0, column=0, padx=5)

        self.btn_ajouter_client = tk.Button(action_frame, text="Ajouter Client", command=self.ajouter_client)
        self.btn_ajouter_client.grid(row=0, column=1, padx=5)

        self.btn_ajouter_produit = tk.Button(action_frame, text="Ajouter Produit", command=self.ajouter_produit)
        self.btn_ajouter_produit.grid(row=0, column=2, padx=5)
        self.btn_ajouter_produit.config(state=tk.DISABLED)

        self.btn_deplacer_produit = tk.Button(action_frame, text="Déplacer Produit", command=self.deplacer_produit)
        self.btn_deplacer_produit.grid(row=0, column=3, padx=5)
        self.btn_deplacer_produit.config(state=tk.DISABLED)


        self.btn_edit = tk.Button(action_frame, text="Edit", command=self.editer_element)
        self.btn_edit.grid(row=0, column=4, padx=5)
        self.btn_edit.config(state=tk.NORMAL)

        self.btn_supprimer_produit = tk.Button(action_frame, text="Supprimer Produit", command=self.supprimer_produit)
        self.btn_supprimer_produit.grid(row=0, column=5, padx=5)
        self.btn_supprimer_produit.config(state=tk.DISABLED)

        # Bouton "Clients" sur une nouvelle ligne, en dessous des autres boutons
        self.btn_clients = tk.Button(action_frame, text="Clients", command=self.ouvrir_fenetre_clients)
        self.btn_clients.grid(row=1, column=0, columnspan=6, pady=10)  # Placé sur une nouvelle ligne avec un padding vertical

        self.btn_lister_produits = tk.Button(action_frame, text="Lister produits", command=self.lister_produits)
        self.btn_lister_produits.grid(row=1, column=2, columnspan=6, pady=10)

        self.btn_historique = tk.Button(action_frame, text="Historique", command=self.consulter_historique)
        self.btn_historique.grid(row=1, column=6, columnspan=6, pady=10)

        # Cadre gauche : Arborescence
        self.left_frame = tk.Frame(self.root)
        self.left_frame.grid(row=1, column=0, padx=10, pady=10, sticky="nsew")

        # Cadre droit : Informations du produit
        self.right_frame = tk.Frame(self.root)
        self.right_frame.grid(row=1, column=1, padx=10, pady=10, sticky="nsew")

        # Arborescence
        self.tree = ttk.Treeview(self.left_frame, height=25)
        self.tree.grid(row=0, column=0, sticky="nsew")
        self.left_frame.grid_columnconfigure(0, weight=1)

        # Fixer une largeur à la colonne principale de l'arborescence
        self.tree.column("#0", width=200)

        # Informations de l'élément sélectionné
        self.details_label = tk.Label(self.right_frame, text="Informations de l'élément sélectionné", anchor='w')
        self.details_label.grid(row=0, column=0, padx=10, pady=10, sticky="n")

        # Créer le contexte de sélection avec le State Pattern
        self.context = SelectionContext(self, controller)

        # Indicateur de réinitialisation de sélection
        self.resetting_selection = False

        # Variables pour stocker l'entrepôt et l'emplacement sélectionnés
        self.entrepot_selectionne = None
        self.emplacement_selectionne = None
        self.produit_selectionne = None

        # Attacher un événement de clic sur l'arborescence
        self.tree.bind("<<TreeviewSelect>>", self.on_tree_select)

        # Afficher les entrepôts et emplacements au démarrage
        self.afficher_arborescence()
    
    def afficher_arborescence(self):
        """
        Affiche l'arborescence des entrepôts et des emplacements.
        """
        # Effacer les anciens éléments de la vue arborescente
        for item in self.tree.get_children():
            self.tree.delete(item)

        # Récupérer les entrepôts du contrôleur et les ajouter à l'arborescence
        entrepots = self.controller.get_entrepots()
        for nom_entrepot, entrepot in entrepots.items():
            # Ajouter l'entrepôt comme élément racine dans l'arborescence
            entrepot_item = self.tree.insert("", "end", text=nom_entrepot, open=True)
            
            # Récupérer les emplacements de chaque entrepôt et les ajouter sous chaque entrepôt
            emplacements = self.controller.get_emplacements(nom_entrepot)
            for emplacement, produit in emplacements.items():
                if produit:  # Si un produit est assigné à cet emplacement
                    self.tree.insert(entrepot_item, "end", text=f"{emplacement} - {produit}")
                else:  # Si l'emplacement est vide
                    self.tree.insert(entrepot_item, "end", text=f"{emplacement} (vide)")

    def on_tree_select(self, event):
        """
        Gère la sélection dans l'arborescence et délègue le traitement au contexte d'état.
        """
        selected_item_id = self.tree.focus()
        selected_text = self.tree.item(selected_item_id)['text']
        parent_item = self.tree.parent(selected_item_id)

        if not parent_item:
            # Si le parent est vide, c'est un entrepôt
            self.entrepot_selectionne = selected_text
            self.emplacement_selectionne = None
            self.produit_selectionne = None
            print(f"Entrepôt sélectionné : {self.entrepot_selectionne}")
            self.details_label.config(text=f"Entrepôt : {self.entrepot_selectionne}")
        else:
            # Si le parent existe, c'est un emplacement ou un produit
            self.entrepot_selectionne = self.tree.item(parent_item)['text']
            emplacement_nom = selected_text.split(" ")[0]
            self.emplacement_selectionne = emplacement_nom

            emplacement = self.controller.entrepots[self.entrepot_selectionne].get_emplacement(emplacement_nom)
            if emplacement and not emplacement.est_vide():
                self.produit_selectionne = emplacement.produit
                print(f"Produit sélectionné : {self.produit_selectionne.nom}")
                self.afficher_details_produit(self.produit_selectionne)
            else:
                self.produit_selectionne = None
                print(f"Emplacement vide sélectionné : {emplacement_nom} dans {self.entrepot_selectionne}")
                self.details_label.config(text="Aucun produit sélectionné.")

        self.context.handle_selection(selected_item_id)


    def ask_lieu_de_chargement(self):
        popup = tk.Tk()
        popup.withdraw()  # Hide the main popup window
        
        lieu_nom = simpledialog.askstring("Lieu de chargement", "Nom société:")
        lieu_adresse = simpledialog.askstring("Lieu de chargement", "Adresse:")
        lieu_CP = simpledialog.askstring("Lieu de chargement", "CP:")
        
        return lieu_nom, lieu_adresse, lieu_CP

    def generer_bon_entree(self):
        """
        Génère un bon d'entrée pour le produit sélectionné.
        """
        lieu_nom, lieu_adresse, lieu_CP = self.ask_lieu_de_chargement()
        if not self.produit_selectionne:
            messagebox.showerror("Erreur", "Aucun produit sélectionné.")
            return

        # Récupérer le client correspondant au nom stocké
        produit = self.produit_selectionne
        client_nom = produit.client
        client = self.controller.get_clients().get(client_nom)

        # Générer le bon d'entrée
        bon_entree_path = generate_bon_entree(
            client_name=client.nom,
            address=client.adresse,
            contact_name=client.nom,
            contact_phone="N/A",  # Placeholder pour le numéro de téléphone
            ref_num=self.produit_selectionne.id,
            description=self.produit_selectionne.description,
            entrepot_name=self.produit_selectionne.entrepot,
            date_entree=self.produit_selectionne.get_date(),  # Utiliser la date d'entrée stockée
            lieu_nom=lieu_nom,
            lieu_adresse=lieu_adresse,
            lieu_CP=lieu_CP
        )

        messagebox.showinfo("Succès", f"Bon d'entrée généré : {bon_entree_path}")



    def afficher_details_produit(self, produit):
        """
        Affiche les détails du produit en récupérant la date d'entrée depuis Firebase via le contrôleur.
        """
        produit_id = produit.id  # Récupérer l'ID du produit sélectionné

        # Demander au contrôleur de récupérer la date d'entrée depuis Firebase
        date_entree = self.controller.recuperer_date_entree(produit_id)

        # Formater les détails du produit à afficher
        details = (
            f"Nom : {produit.nom}\n"
            f"Client : {produit.client}\n"
            f"Description : {produit.description}\n"
            f"Emplacement : {produit.emplacement}\n"
            f"Entrepôt : {produit.entrepot}\n"
            f"Date d'ajout : {date_entree}"  # Afficher la date récupérée depuis Firebase
        )

        # Mettre à jour le label dans la vue
        self.details_label.config(text=details)


    def reset_selection(self):
        """
        Réinitialise la sélection dans l'arborescence.
        """
        # Désélectionner tous les éléments dans l'arborescence
        self.tree.selection_remove(self.tree.selection())
        # Réinitialiser les variables de sélection
        self.entrepot_selectionne = None
        self.emplacement_selectionne = None
        self.produit_selectionne = None
        # Réinitialiser l'interface après la désélection
        self.reset_interface()

    def get_produit_at(self, selected_item_id):
        """
        Récupère le produit à un emplacement donné dans l'arborescence.
        """
        parent_item = self.tree.parent(selected_item_id)
        if parent_item:
            entrepot_selectionne = self.tree.item(parent_item)['text']
            emplacement_nom = self.tree.item(selected_item_id)['text'].split(" ")[0]
            print(f"Récupération du produit à l'emplacement {emplacement_nom} dans l'entrepôt {entrepot_selectionne}")

            emplacement = self.controller.entrepots[entrepot_selectionne].get_emplacement(emplacement_nom)
            
            if emplacement:
                if emplacement.produit:
                    print(f"Produit trouvé : {emplacement.produit.nom}")
                else:
                    print(f"Aucun produit trouvé à l'emplacement {emplacement_nom}")
                return emplacement.produit
            else:
                print(f"Erreur : Emplacement {emplacement_nom} non trouvé dans l'entrepôt {entrepot_selectionne}")
        return None



    def is_product_selected(self, selected_item_id):
        parent_item = self.tree.parent(selected_item_id)
        if parent_item:
            entrepot_selectionne = self.tree.item(parent_item)['text']
            emplacement_nom = self.tree.item(selected_item_id)['text'].split(" ")[0]
            emplacement = self.controller.entrepots[entrepot_selectionne].get_emplacement(emplacement_nom)
            return emplacement and not emplacement.est_vide()  # Retourne True si un produit est présent
        return False

    def is_empty_location(self, selected_item_id):
        parent_item = self.tree.parent(selected_item_id)
        if parent_item:
            entrepot_selectionne = self.tree.item(parent_item)['text']
            emplacement_nom = self.tree.item(selected_item_id)['text'].split(" ")[0]
            emplacement = self.controller.entrepots[entrepot_selectionne].get_emplacement(emplacement_nom)
            return emplacement and emplacement.est_vide()
        return False

    def update_interface_for_selection(self, selected_item_id):
        """
        Met à jour l'interface selon l'élément sélectionné dans l'arborescence.
        """
        parent_item = self.tree.parent(selected_item_id)

        if not parent_item:
            # Si le parent est vide, c'est un entrepôt
            self.btn_edit.config(state=tk.NORMAL)
        else:
            # Si un produit ou un emplacement est sélectionné
            self.btn_ajouter_produit.config(state=tk.NORMAL)
            self.btn_deplacer_produit.config(state=tk.NORMAL)
            self.btn_edit.config(state=tk.NORMAL)
            self.btn_supprimer_produit.config(state=tk.NORMAL)


    def update_interface_for_product_selected(self):
        self.btn_deplacer_produit.config(state=tk.NORMAL)
        self.btn_edit.config(state=tk.NORMAL)  # Activer le bouton d'édition
        self.btn_supprimer_produit.config(state=tk.NORMAL)


    def update_interface_for_nothing_selected(self):
        """
        Met à jour l'interface pour désactiver tous les boutons sauf 'Ajouter Entrepôt' et 'Ajouter Client'.
        """
        self.btn_ajouter_entrepot.config(state=tk.NORMAL)
        self.btn_ajouter_client.config(state=tk.NORMAL)

        # Désactiver tous les autres boutons
        self.btn_ajouter_produit.config(state=tk.DISABLED)
        self.btn_deplacer_produit.config(state=tk.DISABLED)
        self.btn_edit.config(state=tk.DISABLED)
        self.btn_supprimer_produit.config(state=tk.DISABLED)


    def reset_interface(self):
        """
        Réinitialise l'interface utilisateur lorsque l'état change vers NeutralState.
        Cette méthode désactive tous les boutons sauf ceux qui devraient être actifs en NeutralState.
        """
        # Désactiver tous les boutons d'action
        self.btn_ajouter_produit.config(state=tk.DISABLED)
        self.btn_deplacer_produit.config(state=tk.DISABLED)
        self.btn_edit.config(state=tk.DISABLED)
        self.btn_supprimer_produit.config(state=tk.DISABLED)

        # Dans l'état neutre, l'ajout de produit doit être activé si un emplacement vide est sélectionné
        if self.entrepot_selectionne and self.emplacement_selectionne and self.produit_selectionne is None:
            self.btn_ajouter_produit.config(state=tk.NORMAL)
        else:
            # Si un produit est sélectionné, activer les boutons de modification et de déplacement
            if self.produit_selectionne:
                self.btn_deplacer_produit.config(state=tk.NORMAL)
                self.btn_edit.config(state=tk.NORMAL)
                self.btn_supprimer_produit.config(state=tk.NORMAL)


    def confirmer_echange(self, produit_cible, selected_item_id):
        """
        Demande une confirmation à l'utilisateur pour échanger deux produits.
        """
        confirmation = messagebox.askyesno(
            "Échange de produits",
            f"L'emplacement contient déjà le produit {produit_cible.nom}.\n"
            f"Voulez-vous échanger ce produit ?"
        )
        
        if confirmation:
            # Si l'utilisateur confirme, procéder à l'échange
            self.echanger_produits(selected_item_id)
        else:
            print("Échange annulé par l'utilisateur.")
        self.context.set_state(NothingSelectedState())

    def echanger_produits(self, selected_item_id):
        """
        Gère l'échange de produits entre deux emplacements.
        """
        if not self.emplacement_depart:
            print("Erreur : Emplacement de départ non défini.")
            return

        # Récupérer les informations de l'emplacement de départ
        ancien_entrepot = self.emplacement_depart['entrepot']
        ancien_emplacement = self.emplacement_depart['objet_emplacement']

        # Récupérer les informations de l'emplacement cible
        nouvel_entrepot = self.tree.item(self.tree.parent(selected_item_id))['text']
        nouvel_emplacement_nom = self.tree.item(selected_item_id)['text'].split(" ")[0]
        nouvel_emplacement = self.controller.entrepots[nouvel_entrepot].get_emplacement(nouvel_emplacement_nom)

        # Appeler la méthode d'échange dans le contrôleur
        success = self.controller.echanger_produits(
            self.controller.entrepots[ancien_entrepot],
            ancien_emplacement,
            self.controller.entrepots[nouvel_entrepot],
            nouvel_emplacement
        )

        if success:
            print(f"Échange effectué entre {ancien_emplacement.nom} et {nouvel_emplacement_nom}.")
            self.refresh_tree_view()
            self.reset_selection()
        else:
            print("Erreur : L'échange a échoué.")

    def confirm_move(self, selected_item_id):
        """
        Confirme le déplacement du produit vers un nouvel emplacement vide.
        """
        if not self.emplacement_depart:
            print("Erreur : Emplacement de départ non défini.")
            return

        # Récupérer les informations de l'emplacement de départ
        ancien_entrepot = self.emplacement_depart['entrepot']
        ancien_emplacement = self.emplacement_depart['objet_emplacement']
        produit_a_deplacer = ancien_emplacement.produit

        if not produit_a_deplacer:
            print(f"Erreur : Aucun produit à déplacer depuis l'emplacement {ancien_emplacement.nom}.")
            return

        # Récupérer l'emplacement de destination
        nouvel_entrepot = self.tree.item(self.tree.parent(selected_item_id))['text']
        nouvel_emplacement_nom = self.tree.item(selected_item_id)['text'].split(" ")[0]
        nouvel_emplacement = self.controller.entrepots[nouvel_entrepot].get_emplacement(nouvel_emplacement_nom)

        if nouvel_emplacement.est_vide():
            # Déplacer le produit
            self.controller.deplacer_produit(
                ancien_entrepot, ancien_emplacement, nouvel_entrepot, nouvel_emplacement
            )
            print(f"Produit {produit_a_deplacer.nom} déplacé vers l'emplacement {nouvel_emplacement_nom}.")
            self.refresh_tree_view()
            self.reset_selection()
            self.context.set_state(NothingSelectedState())
        else:
            print("Erreur : L'emplacement cible n'est pas vide.")



    def supprimer_produit(self):
        if not self.produit_selectionne:
            messagebox.showerror("Erreur", "Veuillez sélectionner un produit à supprimer.")
            return

        confirmation = messagebox.askyesno(
            "Confirmation", 
            f"Voulez-vous vraiment supprimer le produit {self.produit_selectionne.nom} ?"
        )

        if confirmation:
            produit_id = self.produit_selectionne.id
            #self.generer_bon_sortie()
            self.controller.supprimer_produit(produit_id)
            messagebox.showinfo("Succès", f"Produit {self.produit_selectionne.nom} supprimé avec succès.")
            
            # Rafraîchir l'arborescence après la suppression
            self.refresh_tree_view()


    def deplacer_produit(self):
        """
        Gère le déplacement d'un produit sélectionné vers un nouvel emplacement.
        """

        # Sauvegarder l'emplacement de départ avant d'entrer en MovingProductState
        self.emplacement_depart = {
            'entrepot': self.entrepot_selectionne,
            'objet_emplacement': self.controller.entrepots[self.entrepot_selectionne].get_emplacement(self.emplacement_selectionne)
        }

        # Activer le mode de déplacement
        self.context.set_state(MovingProductState())

    def editer_element(self):
        selected_item_id = self.tree.focus()
        parent_item = self.tree.parent(selected_item_id)
        
        if parent_item:  # C'est un produit
            self.editer_produit()
        else:  # C'est un entrepôt
            self.editer_entrepot()

    def refresh_tree_view(self):
        self.tree.selection_remove(self.tree.selection())
        self.afficher_arborescence()

    def ajouter_entrepot(self):
        """
        Fenêtre pop-up pour ajouter un entrepôt.
        """
        self.popup = tk.Toplevel()
        self.popup.title("Ajouter un Entrepôt")

        tk.Label(self.popup, text="Nom de l'entrepôt:").grid(row=0, column=0)
        tk.Label(self.popup, text="Commune:").grid(row=1, column=0)
        tk.Label(self.popup, text="Nombre d'étages:").grid(row=2, column=0)
        tk.Label(self.popup, text="Emplacements par étage:").grid(row=3, column=0)

        self.nom_entrepot = tk.Entry(self.popup)
        self.commune_entrepot = tk.Entry(self.popup)
        self.nombre_etages = tk.Entry(self.popup)
        self.emplacements_par_etage = tk.Entry(self.popup)

        self.nom_entrepot.grid(row=0, column=1)
        self.commune_entrepot.grid(row=1, column=1)
        self.nombre_etages.grid(row=2, column=1)
        self.emplacements_par_etage.grid(row=3, column=1)

        self.btn_ajouter = tk.Button(self.popup, text="Ajouter", command=self.valider_ajout_entrepot)
        self.btn_ajouter.grid(row=4, columnspan=2)

    def valider_ajout_entrepot(self):
        """
        Valide l'ajout de l'entrepôt dans la base de données.
        """
        nom = self.nom_entrepot.get()
        commune = self.commune_entrepot.get()
        nombre_etages = int(self.nombre_etages.get())
        emplacements_par_etage = int(self.emplacements_par_etage.get())

        if self.controller.ajouter_entrepot(nom, commune, nombre_etages, emplacements_par_etage):
            self.popup.destroy()
            self.refresh_tree_view()  # Rafraîchir la vue après l'ajout d'un entrepôt
        else:
            messagebox.showerror("Erreur", "Entrepôt déjà existant")

    def ajouter_client(self):
        """
        Fenêtre pop-up pour ajouter un client.
        """
        self.popup = tk.Toplevel()
        self.popup.title("Ajouter un Client")

        tk.Label(self.popup, text="Nom du client:").grid(row=0, column=0)
        self.nom_client = tk.Entry(self.popup)
        self.nom_client.grid(row=0, column=1)

        tk.Label(self.popup, text="Adresse:").grid(row=1, column=0)
        self.adresse_client = tk.Entry(self.popup)
        self.adresse_client.grid(row=1, column=1)

        tk.Label(self.popup, text="Nom de la société:").grid(row=2, column=0)
        self.nom_societe_client = tk.Entry(self.popup)
        self.nom_societe_client.grid(row=2, column=1)

        self.btn_ajouter = tk.Button(self.popup, text="Ajouter", command=self.valider_ajout_client)
        self.btn_ajouter.grid(row=3, columnspan=2)

    def valider_ajout_client(self):
        """
        Valide l'ajout du client avec nom, adresse et nom de société.
        """
        nom = self.nom_client.get()
        adresse = self.adresse_client.get()
        nom_societe = self.nom_societe_client.get()

        if self.controller.ajouter_client(nom, adresse, nom_societe):
            self.popup.destroy()
            messagebox.showinfo("Succès", f"Client {nom} ajouté avec succès")
        else:
            messagebox.showerror("Erreur", "Un client avec ce nom existe déjà.")

    def ouvrir_fenetre_clients(self):
        """
        Ouvre une fenêtre avec la liste des clients et permet de les modifier.
        """
        self.popup_clients = tk.Toplevel()
        self.popup_clients.title("Liste des Clients")

        # Créer un tableau pour afficher les clients
        self.tree_clients = ttk.Treeview(self.popup_clients, columns=("Nom", "Adresse", "Nom de Société"), show='headings')
        self.tree_clients.heading("Nom", text="Nom")
        self.tree_clients.heading("Adresse", text="Adresse")
        self.tree_clients.heading("Nom de Société", text="Nom de Société")

        # Remplir le tableau avec les clients actuels
        for nom, client in self.controller.get_clients().items():
            self.tree_clients.insert("", "end", values=(client.nom, client.adresse, client.nom_societe))

        self.tree_clients.pack(padx=10, pady=10)

        # Bouton pour éditer le client sélectionné
        self.btn_modifier_client = tk.Button(self.popup_clients, text="Modifier", command=self.modifier_client)
        self.btn_modifier_client.pack(padx=10, pady=10)

    def modifier_client(self):
        """
        Ouvre une fenêtre pour modifier les informations du client sélectionné.
        """
        selected_item = self.tree_clients.selection()
        if not selected_item:
            messagebox.showerror("Erreur", "Veuillez sélectionner un client.")
            return

        client_values = self.tree_clients.item(selected_item, 'values')
        nom_client = client_values[0]

        # Récupérer le client à partir du contrôleur
        client = self.controller.get_clients()[nom_client]

        # Ouvrir une fenêtre pour modifier les informations du client
        self.popup_modifier_client = tk.Toplevel()
        self.popup_modifier_client.title(f"Modifier le Client : {client.nom}")

        tk.Label(self.popup_modifier_client, text="Nom:").grid(row=0, column=0)
        self.nom_client_edit = tk.Entry(self.popup_modifier_client)
        self.nom_client_edit.grid(row=0, column=1)
        self.nom_client_edit.insert(0, client.nom)

        tk.Label(self.popup_modifier_client, text="Adresse:").grid(row=1, column=0)
        self.adresse_client_edit = tk.Entry(self.popup_modifier_client)
        self.adresse_client_edit.grid(row=1, column=1)
        self.adresse_client_edit.insert(0, client.adresse)

        tk.Label(self.popup_modifier_client, text="Nom de Société:").grid(row=2, column=0)
        self.nom_societe_edit = tk.Entry(self.popup_modifier_client)
        self.nom_societe_edit.grid(row=2, column=1)
        self.nom_societe_edit.insert(0, client.nom_societe)

        self.btn_sauvegarder_client = tk.Button(self.popup_modifier_client, text="Sauvegarder", command=lambda: self.sauvegarder_modifications_client(nom_client))
        self.btn_sauvegarder_client.grid(row=3, columnspan=2, pady=10)

    def sauvegarder_modifications_client(self, nom_client_initial):
        """
        Sauvegarde les modifications effectuées sur un client.
        """
        nouveau_nom = self.nom_client_edit.get()
        nouvelle_adresse = self.adresse_client_edit.get()
        nouveau_nom_societe = self.nom_societe_edit.get()

        # Appeler la méthode du contrôleur pour mettre à jour le client
        success = self.controller.editer_client(nom_client_initial, nouveau_nom, nouvelle_adresse, nouveau_nom_societe)

        if success:
            self.popup_modifier_client.destroy()
            messagebox.showinfo("Succès", "Le client a été mis à jour avec succès.")
            self.refresh_tree_clients()  # Rafraîchir la liste des clients
        else:
            messagebox.showerror("Erreur", "Une erreur est survenue lors de la mise à jour du client.")



    def ajouter_produit(self):
        """
        Fenêtre pop-up pour ajouter un produit dans l'emplacement sélectionné.
        """
        if not self.entrepot_selectionne or not self.emplacement_selectionne:
            messagebox.showerror("Erreur", "Veuillez sélectionner un emplacement vide pour ajouter un produit.")
            return

        # Ouvrir une fenêtre contextuelle pour entrer les détails du produit
        self.popup = tk.Toplevel()
        self.popup.title(f"Ajouter un Produit à l'emplacement {self.emplacement_selectionne}")

        tk.Label(self.popup, text="Nom du produit:").grid(row=0, column=0)
        tk.Label(self.popup, text="Client:").grid(row=1, column=0)
        tk.Label(self.popup, text="Description:").grid(row=2, column=0)

        self.nom_produit = tk.Entry(self.popup)
        self.nom_produit.grid(row=0, column=1)

        # Sélectionner un client à partir d'un menu déroulant
        self.client_produit = tk.StringVar(self.popup)
        clients = list(self.controller.get_clients().keys())
        self.menu_client = tk.OptionMenu(self.popup, self.client_produit, *clients)
        self.menu_client.grid(row=1, column=1)

        # Champ de texte pour la description
        self.description_produit = tk.Text(self.popup, height=5, width=40)
        self.description_produit.grid(row=2, column=1)

        self.btn_ajouter = tk.Button(self.popup, text="Ajouter", command=self.valider_ajout_produit)
        self.btn_ajouter.grid(row=3, columnspan=2)

    def valider_ajout_produit(self):
        """
        Valide l'ajout du produit avec les informations saisies.
        """
        nom = self.nom_produit.get()
        client_nom = self.client_produit.get()
        description = self.description_produit.get("1.0", tk.END).strip()

        if not nom or not client_nom or not description:
            messagebox.showerror("Erreur", "Tous les champs sont obligatoires.")
            return

        # Ajouter le produit via le contrôleur
        produit = self.controller.ajouter_produit(nom, client_nom, description, self.entrepot_selectionne, self.emplacement_selectionne)
        
        if produit:
            self.popup.destroy()
            messagebox.showinfo("Succès", f"Produit {nom} ajouté à l'emplacement {self.emplacement_selectionne}")
            self.refresh_tree_view()
        else:
            messagebox.showerror("Erreur", "L'ajout du produit a échoué.")

    def editer_produit(self):
        """
        Fenêtre pop-up pour éditer un produit sélectionné.
        """
        if not self.produit_selectionne:
            messagebox.showerror("Erreur", "Veuillez sélectionner un produit.")
            return

        # Ouvrir une fenêtre pour éditer les détails du produit
        self.popup = tk.Toplevel()
        self.popup.title(f"Éditer le produit {self.produit_selectionne.nom}")

        tk.Label(self.popup, text="Nom du produit:").grid(row=0, column=0)
        tk.Label(self.popup, text="Description:").grid(row=1, column=0)

        self.nom_produit_edit = tk.Entry(self.popup)
        self.nom_produit_edit.grid(row=0, column=1)
        self.nom_produit_edit.insert(0, self.produit_selectionne.nom)

        self.description_produit_edit = tk.Text(self.popup, height=5, width=40)
        self.description_produit_edit.grid(row=1, column=1)
        self.description_produit_edit.insert(tk.END, self.produit_selectionne.description)

        self.btn_ajouter = tk.Button(self.popup, text="Sauvegarder", command=self.valider_edition_produit)
        self.btn_ajouter.grid(row=2, columnspan=2)

    def valider_edition_produit(self):
        """
        Valide et sauvegarde les modifications apportées au produit.
        """
        nom = self.nom_produit_edit.get()
        description = self.description_produit_edit.get("1.0", tk.END).strip()

        produit_id = self.produit_selectionne.id
        success = self.controller.editer_produit(produit_id, nom, description)

        if success:
            self.popup.destroy()
            messagebox.showinfo("Succès", "Produit mis à jour avec succès.")
            self.refresh_tree_view()
        else:
            messagebox.showerror("Erreur", "La mise à jour du produit a échoué.")

    def editer_entrepot(self):
        """
        Fenêtre pop-up pour éditer un entrepôt sélectionné.
        """


        self.popup = tk.Toplevel()
        self.popup.title(f"Éditer l'entrepôt {self.entrepot_selectionne}")

        entrepot = self.controller.entrepots[self.entrepot_selectionne]

        tk.Label(self.popup, text="Nom de l'entrepôt:").grid(row=0, column=0)
        tk.Label(self.popup, text="Commune:").grid(row=1, column=0)
        tk.Label(self.popup, text="Nombre d'étages:").grid(row=2, column=0)
        tk.Label(self.popup, text="Emplacements par étage:").grid(row=3, column=0)

        self.nom_entrepot_edit = tk.Entry(self.popup)
        self.nom_entrepot_edit.grid(row=0, column=1)
        self.nom_entrepot_edit.insert(0, entrepot.nom)

        self.commune_entrepot_edit = tk.Entry(self.popup)
        self.commune_entrepot_edit.grid(row=1, column=1)
        self.commune_entrepot_edit.insert(0, entrepot.commune)

        self.nombre_etages_edit = tk.Entry(self.popup)
        self.nombre_etages_edit.grid(row=2, column=1)
        self.nombre_etages_edit.insert(0, entrepot.nombre_etages)

        self.emplacements_par_etage_edit = tk.Entry(self.popup)
        self.emplacements_par_etage_edit.grid(row=3, column=1)
        self.emplacements_par_etage_edit.insert(0, entrepot.emplacements_par_etage)

        self.btn_ajouter = tk.Button(self.popup, text="Sauvegarder", command=self.valider_edition_entrepot)
        self.btn_ajouter.grid(row=4, columnspan=2)

    def valider_edition_entrepot(self):
        """
        Valide et sauvegarde les modifications apportées à l'entrepôt.
        """
        nouveau_nom = self.nom_entrepot_edit.get()
        commune = self.commune_entrepot_edit.get()
        nombre_etages = int(self.nombre_etages_edit.get())
        emplacements_par_etage = int(self.emplacements_par_etage_edit.get())

        success = self.controller.editer_entrepot(self.entrepot_selectionne, nouveau_nom, commune, nombre_etages, emplacements_par_etage)

        if success:
            self.popup.destroy()
            messagebox.showinfo("Succès", "Entrepôt mis à jour avec succès.")
            self.refresh_tree_view()
        else:
            messagebox.showerror("Erreur", "La mise à jour de l'entrepôt a échoué.")

        self.refresh_tree_view()
    
    def lister_produits(self):
        """
        Affiche une fenêtre listant tous les produits non vides et permet de les sélectionner pour générer un bon.
        """
        self.popup_lister_produits = tk.Toplevel()
        self.popup_lister_produits.title("Lister les Produits")

        # Récupérer la liste des produits non vides
        produits_non_vides = []
        for entrepot in self.controller.get_entrepots().values():
            produits_non_vides += entrepot.liste_emplacements_pleins()

        self.check_vars = {}  # Réinitialiser les variables de sélection

        # Créer une liste déroulante avec des cases à cocher
        for index, produit in enumerate(produits_non_vides):
            check_var = tk.BooleanVar()
            self.check_vars[produit] = check_var  # Stocker l'objet produit comme clé
            tk.Checkbutton(
                self.popup_lister_produits,
                text=f"{produit.nom} - {produit.description}",
                variable=check_var
            ).pack(anchor="w")

        # Ajouter des boutons pour générer les bons
        tk.Button(
            self.popup_lister_produits,
            text="Générer Bon d'Entrée",
            command=self.generer_bon_entree
        ).pack(pady=10)

        tk.Button(
            self.popup_lister_produits,
            text="Générer Bon de Sortie",
            command=self.generer_bon_sortie
        ).pack(pady=10)

    def generer_bon_entree(self):
        """
        Génère un bon d'entrée pour les produits sélectionnés.
        """
        produits = self.get_selected_products()
        if not produits:
            messagebox.showerror("Erreur", "Aucun produit sélectionné.")
            return

        # Récupérer les dates d'entrée depuis Firebase et mettre à jour chaque produit
        for produit in produits:
            produit.date_entree = self.controller.recuperer_date_entree(produit.id)

        entrepot = produits[0].entrepot  # Supposons que tous les produits sont dans le même entrepôt

        try:
            output_path = generate_bon_entree(produits, entrepot, self.controller)  # Inclure le contrôleur
            messagebox.showinfo("Succès", f"Bon d'entrée généré : {output_path}")
        except Exception as e:
            messagebox.showerror("Erreur", f"Une erreur est survenue : {str(e)}")


    def generer_bon_sortie(self):
        """
        Génère un bon de sortie pour les produits sélectionnés.
        Demande à l'utilisateur de choisir un client ou d'en ajouter un nouveau.
        """
        produits = self.get_selected_products()
        if not produits:
            messagebox.showerror("Erreur", "Aucun produit sélectionné.")
            return

        # Ouvrir une fenêtre pour sélectionner ou ajouter un client
        self.popup_client = tk.Toplevel()
        self.popup_client.title("Choisir un client")

        tk.Label(self.popup_client, text="Sélectionnez un client ou ajoutez-en un nouveau :").pack(pady=10)

        # Liste des clients dans un menu déroulant
        clients = list(self.controller.get_clients().values())  # Récupérer les objets Client
        self.client_var = tk.StringVar(self.popup_client)

        if clients:
            self.client_menu = ttk.Combobox(self.popup_client, textvariable=self.client_var)
            self.client_menu['values'] = [client.nom for client in clients]
            self.client_menu.pack(pady=10)
        else:
            tk.Label(self.popup_client, text="Aucun client existant. Veuillez en ajouter un.").pack()

        # Bouton pour ajouter un nouveau client
        tk.Button(self.popup_client, text="Ajouter un Client", command=self.ajouter_client_pour_bon).pack(pady=10)

        # Boutons de validation et annulation
        tk.Button(
            self.popup_client,
            text="Valider",
            command=lambda: self.valider_client_pour_bon_sortie(produits)
        ).pack(pady=10)
        tk.Button(self.popup_client, text="Annuler", command=self.popup_client.destroy).pack(pady=10)


    def ajouter_client_pour_bon(self):
        """
        Ouvre une fenêtre pour ajouter un nouveau client à la base de données.
        """
        self.popup_add_client = tk.Toplevel()
        self.popup_add_client.title("Ajouter un Client")

        tk.Label(self.popup_add_client, text="Nom du client:").grid(row=0, column=0)
        self.nom_client_entry = tk.Entry(self.popup_add_client)
        self.nom_client_entry.grid(row=0, column=1)

        tk.Label(self.popup_add_client, text="Adresse:").grid(row=1, column=0)
        self.adresse_client_entry = tk.Entry(self.popup_add_client)
        self.adresse_client_entry.grid(row=1, column=1)

        tk.Label(self.popup_add_client, text="Nom de société:").grid(row=2, column=0)
        self.nom_societe_client_entry = tk.Entry(self.popup_add_client)
        self.nom_societe_client_entry.grid(row=2, column=1)

        tk.Button(
            self.popup_add_client,
            text="Ajouter",
            command=self.valider_ajout_client_pour_bon
        ).grid(row=3, columnspan=2, pady=10)

    def valider_ajout_client_pour_bon(self):
        """
        Valide l'ajout d'un nouveau client dans la base de données et sélectionne ce client.
        """
        nom = self.nom_client_entry.get()
        adresse = self.adresse_client_entry.get()
        nom_societe = self.nom_societe_client_entry.get()

        if not nom:
            messagebox.showerror("Erreur", "Le nom du client est obligatoire.")
            return

        success = self.controller.ajouter_client(nom, adresse, nom_societe)
        if success:
            messagebox.showinfo("Succès", f"Client {nom} ajouté avec succès.")
            self.popup_add_client.destroy()

            # Mettre à jour le menu déroulant avec le nouveau client
            clients = list(self.controller.get_clients().values())
            self.client_menu['values'] = [client.nom for client in clients]
            self.client_var.set(nom)  # Sélectionner automatiquement le nouveau client

            # Relancer la validation avec le nouveau client
            produits = self.get_selected_products()
            self.valider_client_pour_bon_sortie(produits)
        else:
            messagebox.showerror("Erreur", f"Le client {nom} existe déjà.")

    def valider_client_pour_bon_sortie(self, produits):
        """
        Valide le client sélectionné ou ajouté pour générer le bon de sortie.
        """
        client_nom = self.client_var.get()
        if not client_nom:
            messagebox.showerror("Erreur", "Veuillez sélectionner ou ajouter un client.")
            return

        # Utiliser la méthode existante pour récupérer les données du client
        client_data = self.controller.recuperer_data_client(client_nom)
        if not client_data or client_data["nom"] == "Nom inconnu":
            messagebox.showerror("Erreur", "Le client sélectionné est introuvable.")
            return

        # Récupérer les dates d'entrée depuis Firebase et mettre à jour chaque produit
        for produit in produits:
            produit.date_entree = self.controller.recuperer_date_entree(produit.id)

        # Générer le bon de sortie
        entrepot = produits[0].entrepot  # Supposons que tous les produits sont dans le même entrepôt
        output_path = generate_bon_sortie(produits, entrepot, client_data)

        # Afficher une notification de succès pour le bon généré
        messagebox.showinfo("Succès", f"Bon de sortie généré : {output_path}")

        self.popup_client.destroy()

        # Demander confirmation pour supprimer les produits
        confirmation_suppression = messagebox.askyesno(
            "Confirmation de suppression",
            "Souhaitez-vous supprimer les produits listés dans le bon de sortie ?"
        )
        if confirmation_suppression:
            for produit in produits:
                self.controller.supprimer_produit(produit.id)
            messagebox.showinfo("Succès", "Produits supprimés avec succès.")
            self.refresh_tree_view()  # Rafraîchir l'interface après suppression



    def get_selected_products(self):
        """
        Récupère les objets produits sélectionnés avec leurs informations à jour depuis Firebase.
        """
        selected_products = []
        for produit, var in self.check_vars.items():
            if var.get():
                # Récupérer les données à jour depuis Firebase pour chaque produit sélectionné
                date_entree = self.controller.recuperer_date_entree(produit.id)
                print(date_entree)
                produit.date_entree = date_entree  # Mettre à jour l'objet produit avec la date d'entrée
                selected_products.append(produit)
        return selected_products


    def consulter_historique(self):
        """
        Ouvre une fenêtre pour afficher l'historique des produits supprimés.
        """
        produits_supprimes = self.controller.get_historique_produits_supprimes()

        # Fenêtre popup
        self.popup_historique = tk.Toplevel()
        self.popup_historique.title("Historique des Produits Supprimés")

        # Tableau
        tree_historique = ttk.Treeview(self.popup_historique, columns=(
            'id', 'nom', 'client_nom', 'description', 'entrepot_nom', 'emplacement', 'date_entree', 'date_depart', 'numero_facture'
        ), show='headings', height=20)

        tree_historique.heading('id', text="ID")
        tree_historique.heading('nom', text="Nom")
        tree_historique.heading('client_nom', text="Client")
        tree_historique.heading('description', text="Description")
        tree_historique.heading('entrepot_nom', text="Entrepôt")
        tree_historique.heading('emplacement', text="Emplacement")
        tree_historique.heading('date_entree', text="Date d'Entrée")
        tree_historique.heading('date_depart', text="Date de Sortie")
        tree_historique.heading('numero_facture', text="Numéro de Facture")

        tree_historique.column('id', width=100)
        tree_historique.column('nom', width=150)
        tree_historique.column('client_nom', width=150)
        tree_historique.column('description', width=250)
        tree_historique.column('entrepot_nom', width=150)
        tree_historique.column('emplacement', width=100)
        tree_historique.column('date_entree', width=120)
        tree_historique.column('date_depart', width=120)
        tree_historique.column('numero_facture', width=120)

        # Insérer les données
        # Insérer les données
        for produit in produits_supprimes:
            tree_historique.insert('', 'end', values=(
                produit.get('id', 'ID inconnu'),  # ID
                produit.get('nom', 'Nom inconnu'),  # Nom
                produit.get('client_nom', 'Client inconnu'),  # Client
                produit.get('description', 'Description non spécifiée'),  # Description
                produit.get('entrepot_nom', 'Entrepôt inconnu'),  # Entrepôt
                produit.get('emplacement', 'Emplacement inconnu'),  # Emplacement
                produit.get('date_entree', 'Date inconnue'),  # Date d'entrée
                produit.get('date_depart', 'Date inconnue'),  # Date de sortie
                produit.get('numero_facture', 'Non disponible')  # Numéro de facture
            ))


        tree_historique.pack(fill='both', expand=True, padx=10, pady=10)

        # Bouton de fermeture
        btn_fermer = tk.Button(self.popup_historique, text="Fermer", command=self.popup_historique.destroy)
        btn_fermer.pack(pady=10)





if __name__ == "__main__":
    root = tk.Tk()
    controller = Controller()
    app = View(root, controller)
    root.mainloop()
