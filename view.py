import tkinter as tk
from tkinter import ttk, messagebox
from controller import Controller
from selection_context import SelectionContext
from state import NeutralState, ProductSelectedState, MovingProductState

class View:
    def __init__(self, root, controller):
        self.controller = controller
        self.root = root
        self.root.title("Gestion des Entrepôts")

        # Créer le contexte de sélection avec le State Pattern
        self.context = SelectionContext(self)

        # Indicateur de réinitialisation de sélection
        self.resetting_selection = False

        # Agrandir la fenêtre principale
        self.root.geometry("1200x800")  # Agrandit la fenêtre

        # Variables pour stocker l'entrepôt et l'emplacement sélectionnés
        self.entrepot_selectionne = None
        self.emplacement_selectionne = None
        self.produit_selectionne = None

        # Cadre pour les actions
        action_frame = tk.Frame(root)
        action_frame.pack(pady=10)

        # Bouton pour ajouter un entrepôt
        self.btn_ajouter_entrepot = tk.Button(action_frame, text="Ajouter Entrepôt", command=self.ajouter_entrepot)
        self.btn_ajouter_entrepot.grid(row=0, column=0, padx=5)

        # Bouton pour ajouter un client
        self.btn_ajouter_client = tk.Button(action_frame, text="Ajouter Client", command=self.ajouter_client)
        self.btn_ajouter_client.grid(row=0, column=1, padx=5)

        # Bouton pour ajouter un produit
        self.btn_ajouter_produit = tk.Button(action_frame, text="Ajouter Produit", command=self.ajouter_produit)
        self.btn_ajouter_produit.grid(row=0, column=2, padx=5)
        self.btn_ajouter_produit.config(state=tk.DISABLED)  # Désactivé par défaut

        # Bouton pour déplacer un produit
        self.btn_deplacer_produit = tk.Button(action_frame, text="Déplacer Produit", command=self.deplacer_produit)
        self.btn_deplacer_produit.grid(row=0, column=3, padx=5)
        self.btn_deplacer_produit.config(state=tk.DISABLED)  # Désactivé par défaut

        # Vue arborescente pour les entrepôts
        self.tree = ttk.Treeview(root)
        self.tree.pack(pady=20, fill="both", expand=True)
        self.tree.heading("#0", text="Entrepôts", anchor='w')

        # Attacher un événement de clic sur l'arborescence
        self.tree.bind("<<TreeviewSelect>>", self.on_tree_select)

        # Afficher les entrepôts et emplacements au démarrage
        self.afficher_arborescence()

    def on_tree_select(self, event):
        # Ignorer les événements de sélection pendant la réinitialisation
        if self.resetting_selection:
            return
        
        # Récupérer l'identifiant de l'élément sélectionné dans l'arborescence
        selected_item_id = self.tree.focus()  # Utiliser l'identifiant de l'élément
        item_data = self.tree.item(selected_item_id)  # Obtenir les données de l'élément

        # Déléguer la gestion de la sélection au contexte en passant l'identifiant
        self.context.handle_selection(selected_item_id)  # Passer l'identifiant de l'élément


    def is_product_selected(self, selected_item_id):
        """
        Vérifie si l'élément sélectionné est un produit.
        """
        parent_item = self.tree.parent(selected_item_id)
        if parent_item:
            entrepot_selectionne = self.tree.item(parent_item)['text']
            emplacement_nom = self.tree.item(selected_item_id)['text'].split(" ")[0]  # Utiliser l'identifiant pour récupérer le texte
            emplacement = self.controller.entrepots[entrepot_selectionne].get_emplacement(emplacement_nom)
            if emplacement and not emplacement.est_vide():
                self.entrepot_selectionne = entrepot_selectionne
                self.emplacement_selectionne = emplacement_nom
                self.produit_selectionne = emplacement.produit
                return True
        return False

    def is_empty_location(self, selected_item_id):
        """
        Vérifie si l'élément sélectionné est un emplacement vide.
        """
        parent_item = self.tree.parent(selected_item_id)
        if parent_item:
            entrepot_selectionne = self.tree.item(parent_item)['text']
            emplacement_nom = self.tree.item(selected_item_id)['text'].split(" ")[0]  # Utiliser l'identifiant pour récupérer le texte
            emplacement = self.controller.entrepots[entrepot_selectionne].get_emplacement(emplacement_nom)
            return emplacement and emplacement.est_vide()
        return False

    def update_interface_for_selection(self, selected_item):
        """
        Met à jour l'interface pour l'élément sélectionné.
        """
        self.btn_ajouter_produit.config(state=tk.DISABLED)
        self.btn_deplacer_produit.config(state=tk.NORMAL)

    def update_interface_for_product_selected(self):
        """
        Met à jour l'interface lorsqu'un produit est sélectionné.
        """
        self.btn_deplacer_produit.config(state=tk.NORMAL)

    def update_interface_for_moving_product(self):
        """
        Met à jour l'interface pour le déplacement d'un produit.
        """
        self.btn_ajouter_produit.config(state=tk.DISABLED)
        self.btn_deplacer_produit.config(state=tk.DISABLED)
        messagebox.showinfo("Déplacement", "Sélectionnez un nouvel emplacement vide.")

    def activate_move_mode(self):
        """
        Active le mode de déplacement de produit.
        """
        self.btn_ajouter_produit.config(state=tk.DISABLED)
        self.btn_deplacer_produit.config(state=tk.DISABLED)
        messagebox.showinfo("Déplacement", "Sélectionnez un nouvel emplacement vide pour déplacer le produit.")

    def confirm_move(self, selected_item_id):
        """
        Confirme le déplacement du produit vers un nouvel emplacement.
        """
        selected_item_data = self.tree.item(selected_item_id)
        nouvel_entrepot_selectionne = self.tree.item(self.tree.parent(selected_item_id))['text']
        nouvel_emplacement_nom = selected_item_data['text'].split(" ")[0]
        
        emplacement_cible = self.controller.entrepots[nouvel_entrepot_selectionne].get_emplacement(nouvel_emplacement_nom)
        emplacement_source = self.controller.entrepots[self.entrepot_selectionne].get_emplacement(self.emplacement_selectionne)

        if emplacement_cible.est_vide():
            # Déplacement simple si l'emplacement est vide
            success = self.controller.deplacer_produit(
                self.entrepot_selectionne, emplacement_source,
                nouvel_entrepot_selectionne, emplacement_cible
            )
            if success:
                messagebox.showinfo("Succès", f"Produit {self.produit_selectionne.nom} déplacé avec succès.")
                self.reset_selection()
                self.refresh_tree_view()
            else:
                messagebox.showerror("Erreur", "Le déplacement du produit a échoué.")
        else:
            # Si l'emplacement est occupé, proposer un échange
            produit_cible = emplacement_cible.produit
            confirmation = messagebox.askyesno(
                "Échange de produits",
                f"L'emplacement {nouvel_emplacement_nom} contient déjà le produit {produit_cible.nom}.\n"
                f"Voulez-vous échanger {self.produit_selectionne.nom} avec {produit_cible.nom} ?"
            )
            if confirmation:
                success = self.controller.echanger_produits(
                    self.controller.entrepots[self.entrepot_selectionne],
                    emplacement_source,
                    self.controller.entrepots[nouvel_entrepot_selectionne],
                    emplacement_cible
                )
                if success:
                    messagebox.showinfo("Succès", f"Échange effectué entre {self.emplacement_selectionne} et {nouvel_emplacement_nom}.")
                    self.reset_selection()
                    self.refresh_tree_view()
                else:
                    messagebox.showerror("Erreur", "L'échange de produits a échoué.")


    def reset_selection(self):
        """
        Réinitialise la sélection.
        """
        # Vérifier si la réinitialisation est déjà en cours ou si on est déjà dans l'état neutre
        if self.resetting_selection:
            print("Réinitialisation déjà en cours, retour à la méthode.")
            return
        
        # Vérifier si on est déjà dans l'état NeutralState pour éviter de rafraîchir en boucle
        if isinstance(self.context.state, NeutralState):
            print("Déjà en état NeutralState, pas de réinitialisation nécessaire.")
            return

        print("Début de la réinitialisation de la sélection.")
        self.resetting_selection = True

        # Désactiver les événements de sélection pour éviter les boucles
        self.tree.unbind("<<TreeviewSelect>>")

        # Réinitialiser les variables de sélection
        self.entrepot_selectionne = None
        self.emplacement_selectionne = None
        self.produit_selectionne = None

        # Réinitialiser l'état dans le contexte
        self.context.set_state(NeutralState())

        # Effacer la sélection dans l'arborescence
        self.tree.selection_remove(self.tree.selection())  # Désélectionner tous les éléments
        self.reset_interface()

        # Réactiver les événements de sélection après la réinitialisation
        self.tree.bind("<<TreeviewSelect>>", self.on_tree_select)

        print("Fin de la réinitialisation de la sélection.")
        self.resetting_selection = False

    def reset_interface(self):
        """
        Réinitialise l'interface.
        """
        self.btn_ajouter_produit.config(state=tk.DISABLED)
        self.btn_deplacer_produit.config(state=tk.DISABLED)

    def afficher_arborescence(self):
        """
        Affiche l'arborescence des entrepôts et des emplacements.
        """
        # Effacer les anciens éléments de la vue arborescente
        for item in self.tree.get_children():
            self.tree.delete(item)

        entrepots = self.controller.get_entrepots()
        for nom_entrepot, entrepot in entrepots.items():
            entrepot_item = self.tree.insert("", "end", text=nom_entrepot, open=True)
            emplacements = self.controller.get_emplacements(nom_entrepot)
            for emplacement, produit in emplacements.items():
                if produit:  # Si un produit est assigné à cet emplacement
                    self.tree.insert(entrepot_item, "end", text=f"{emplacement} - {produit}")
                else:  # Si l'emplacement est vide
                    self.tree.insert(entrepot_item, "end", text=f"{emplacement} (vide)")

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
        Valide l'ajout de l'entrepôt.
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
        Valide l'ajout du client.
        """
        nom = self.nom_client.get()

        if self.controller.ajouter_client(nom):
            self.popup.destroy()
            messagebox.showinfo("Succès", f"Client {nom} ajouté")
        else:
            messagebox.showerror("Erreur", "Client déjà existant")

    def ajouter_produit(self):
        """
        Fenêtre pop-up pour ajouter un produit.
        """
        if not self.entrepot_selectionne or not self.emplacement_selectionne:
            messagebox.showerror("Erreur", "Veuillez sélectionner un emplacement vide.")
            return

        # Fenêtre pop-up pour ajouter un produit
        self.popup = tk.Toplevel()
        self.popup.title(f"Ajouter un Produit à l'emplacement {self.emplacement_selectionne}")

        tk.Label(self.popup, text="Nom du produit:").grid(row=0, column=0)
        tk.Label(self.popup, text="Nom du client:").grid(row=1, column=0)
        tk.Label(self.popup, text="Description:").grid(row=2, column=0)

        self.nom_produit = tk.Entry(self.popup)
        self.nom_client_produit = tk.Entry(self.popup)
        self.description_produit = tk.Text(self.popup, height=5, width=40)  # Champ de texte plus grand pour la description

        self.nom_produit.grid(row=0, column=1)
        self.nom_client_produit.grid(row=1, column=1)
        self.description_produit.grid(row=2, column=1)

        self.btn_ajouter = tk.Button(self.popup, text="Ajouter", command=self.valider_ajout_produit)
        self.btn_ajouter.grid(row=3, columnspan=2)

    def valider_ajout_produit(self):
        """
        Valide l'ajout du produit.
        """
        nom = self.nom_produit.get()
        client_nom = self.nom_client_produit.get()
        description = self.description_produit.get("1.0", tk.END).strip()  # Récupère tout le texte du champ Text

        if not self.entrepot_selectionne or not self.emplacement_selectionne:
            messagebox.showerror("Erreur", "Veuillez sélectionner un emplacement vide.")
            return

        produit = self.controller.ajouter_produit(nom, client_nom, description, self.entrepot_selectionne, self.emplacement_selectionne)

        if produit:
            self.popup.destroy()
            messagebox.showinfo("Succès", f"Produit {nom} ajouté à l'emplacement {self.emplacement_selectionne} dans {self.entrepot_selectionne}")
            self.refresh_tree_view()  # Mettre à jour l'arborescence après l'ajout du produit
        else:
            messagebox.showerror("Erreur", "Client ou Entrepôt invalide")

    def deplacer_produit(self):
        """
        Gère le déplacement d'un produit sélectionné vers un nouvel emplacement.
        """
        if not self.entrepot_selectionne or not self.emplacement_selectionne or not self.produit_selectionne:
            messagebox.showerror("Erreur", "Veuillez sélectionner un produit à déplacer.")
            return

        # Activer le mode de déplacement
        self.context.handle_action()

    def refresh_tree_view(self):
        """
        Méthode pour rafraîchir la vue arborescente après chaque opération.
        """
        self.tree.selection_remove(self.tree.selection())  # Désélectionner tous les éléments
        self.afficher_arborescence()  # Réafficher l'arborescence pour refléter les changements

if __name__ == "__main__":
    root = tk.Tk()
    controller = Controller()
    app = View(root, controller)
    root.mainloop()
