import tkinter as tk
from tkinter import ttk, messagebox
from controller import Controller
from selection_context import SelectionContext
from state import NeutralState, ProductSelectedState, MovingProductState, AddingProductState, NothingSelectedState

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
        self.btn_edit.config(state=tk.DISABLED)

        self.btn_supprimer_produit = tk.Button(action_frame, text="Supprimer Produit", command=self.supprimer_produit)
        self.btn_supprimer_produit.grid(row=0, column=5, padx=5)
        self.btn_supprimer_produit.config(state=tk.DISABLED)

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
        self.tree.column("#0", width=150)

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

        # Vérifier si l'élément sélectionné est un emplacement vide ou un produit
        parent_item = self.tree.parent(selected_item_id)

        if parent_item:
            # Il s'agit d'un produit ou d'un emplacement, récupérer l'entrepôt et l'emplacement sélectionnés
            self.entrepot_selectionne = self.tree.item(parent_item)['text']
            emplacement_nom = self.tree.item(selected_item_id)['text'].split(" ")[0]
            self.emplacement_selectionne = emplacement_nom

            # Vérifier si un produit est sélectionné à cet emplacement
            emplacement = self.controller.entrepots[self.entrepot_selectionne].get_emplacement(emplacement_nom)
            if emplacement and not emplacement.est_vide():
                self.produit_selectionne = emplacement.produit  # Mettre à jour le produit sélectionné
                print(f"Produit sélectionné : {self.produit_selectionne.nom}")
            else:
                self.produit_selectionne = None  # Aucune sélection de produit
                print(f"Emplacement vide sélectionné : {emplacement_nom} dans {self.entrepot_selectionne}")

        # Déléguer la gestion de la sélection au contexte d'état
        self.context.handle_selection(selected_item_id)


    def afficher_details_produit(self, produit):
        details = (
            f"Nom : {produit.nom}\n"
            f"Client : {produit.client}\n"
            f"Description : {produit.description}\n"
            f"Emplacement : {produit.emplacement}\n"
            f"Entrepôt : {produit.entrepot}\n"
            f"Date d'ajout : {produit.date.strftime('%d/%m/%Y')}"
        )
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

    def update_interface_for_selection(self, selected_item):
        self.btn_ajouter_produit.config(state=tk.DISABLED)
        self.btn_deplacer_produit.config(state=tk.NORMAL)
        self.btn_edit.config(state=tk.NORMAL)  # Activer le bouton d'édition
        self.btn_supprimer_produit.config(state=tk.NORMAL)  # Activer le bouton suppression

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
            self.controller.supprimer_produit(produit_id)
            messagebox.showinfo("Succès", f"Produit {self.produit_selectionne.nom} supprimé avec succès.")
            
            # Rafraîchir l'arborescence après la suppression
            self.refresh_tree_view()

    def ajouter_produit(self):
        if not self.entrepot_selectionne or not self.emplacement_selectionne:
            messagebox.showerror("Erreur", "Veuillez sélectionner un emplacement vide pour ajouter un produit.")
            return

        # Changer l'état vers AddingProductState
        self.context.set_state(AddingProductState())

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

        self.btn_ajouter = tk.Button(self.popup, text="Ajouter", command=self.valider_ajout_client)
        self.btn_ajouter.grid(row=1, columnspan=2)

    def valider_ajout_client(self):
        """
        Valide l'ajout du client dans la base de données.
        """
        nom = self.nom_client.get()

        if self.controller.ajouter_client(nom):
            self.popup.destroy()
            messagebox.showinfo("Succès", f"Client {nom} ajouté")
        else:
            messagebox.showerror("Erreur", "Client déjà existant")

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
        if not self.entrepot_selectionne:
            messagebox.showerror("Erreur", "Veuillez sélectionner un entrepôt.")
            return

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




if __name__ == "__main__":
    root = tk.Tk()
    controller = Controller()
    app = View(root, controller)
    root.mainloop()
