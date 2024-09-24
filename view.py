# View.py

import tkinter as tk
from tkinter import ttk, messagebox
from controller import Controller

class View:
    def __init__(self, root, controller):
        self.controller = controller
        self.root = root
        self.root.title("Gestion des Entrepôts")

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
        # Récupérer l'élément sélectionné dans l'arborescence
        selected_item = self.tree.focus()
        item_data = self.tree.item(selected_item)
        parent_item = self.tree.parent(selected_item)
        
        if parent_item:  # Parent non vide, donc c'est un emplacement
            self.entrepot_selectionne = self.tree.item(parent_item)['text']
            emplacement_nom = item_data['text'].split(" ")[0]  # Récupérer uniquement le nom de l'emplacement sans (vide) ou - produit
            
            # Récupérer l'objet Emplacement depuis le contrôleur
            self.emplacement_selectionne = self.controller.entrepots[self.entrepot_selectionne].get_emplacement(emplacement_nom)

            # Vérifier si l'emplacement est vide ou non
            if self.emplacement_selectionne and self.emplacement_selectionne.est_vide():
                self.produit_selectionne = None
                self.btn_ajouter_produit.config(state=tk.NORMAL)
                self.btn_deplacer_produit.config(state=tk.DISABLED)
            else:
                self.produit_selectionne = self.emplacement_selectionne.produit
                self.btn_ajouter_produit.config(state=tk.DISABLED)
                self.btn_deplacer_produit.config(state=tk.NORMAL)
        else:  # C'est un entrepôt, désactiver les boutons liés aux emplacements
            self.entrepot_selectionne = item_data['text']
            self.emplacement_selectionne = None
            self.produit_selectionne = None
            self.btn_ajouter_produit.config(state=tk.DISABLED)
            self.btn_deplacer_produit.config(state=tk.DISABLED)

    def ajouter_entrepot(self):
        # Fenêtre pop-up pour ajouter un entrepôt
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
        nom = self.nom_entrepot.get()
        commune = self.commune_entrepot.get()
        nombre_etages = int(self.nombre_etages.get())
        emplacements_par_etage = int(self.emplacements_par_etage.get())

        if self.controller.ajouter_entrepot(nom, commune, nombre_etages, emplacements_par_etage):
            self.popup.destroy()
            self.afficher_arborescence()
        else:
            messagebox.showerror("Erreur", "Entrepôt déjà existant")

    def ajouter_client(self):
        # Fenêtre pop-up pour ajouter un client
        self.popup = tk.Toplevel()
        self.popup.title("Ajouter un Client")

        tk.Label(self.popup, text="Nom du client:").grid(row=0, column=0)
        self.nom_client = tk.Entry(self.popup)
        self.nom_client.grid(row=0, column=1)

        self.btn_ajouter = tk.Button(self.popup, text="Ajouter", command=self.valider_ajout_client)
        self.btn_ajouter.grid(row=1, columnspan=2)

    def valider_ajout_client(self):
        nom = self.nom_client.get()

        if self.controller.ajouter_client(nom):
            self.popup.destroy()
            messagebox.showinfo("Succès", f"Client {nom} ajouté")
        else:
            messagebox.showerror("Erreur", "Client déjà existant")

    def ajouter_produit(self):
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
            self.afficher_arborescence()  # Mettre à jour l'arborescence après l'ajout du produit
        else:
            messagebox.showerror("Erreur", "Client ou Entrepôt invalide")

    def deplacer_produit(self):
        if not self.entrepot_selectionne or not self.emplacement_selectionne or not self.produit_selectionne:
            messagebox.showerror("Erreur", "Veuillez sélectionner un produit à déplacer.")
            return

        # Demander à l'utilisateur de sélectionner un nouvel emplacement vide
        self.popup = tk.Toplevel()
        self.popup.title(f"Déplacer le Produit {self.produit_selectionne} dans {self.entrepot_selectionne}")

        tk.Label(self.popup, text=f"Veuillez sélectionner un emplacement vide pour déplacer {self.produit_selectionne}.").pack(pady=10)
        self.tree.bind("<<TreeviewSelect>>", self.selectionner_nouvel_emplacement)

    def selectionner_nouvel_emplacement(self, event):
        selected_item = self.tree.focus()
        item_data = self.tree.item(selected_item)
        parent_item = self.tree.parent(selected_item)

        if parent_item:
            nouvel_entrepot_selectionne = self.tree.item(parent_item)['text']
            nouvel_emplacement_nom = item_data['text'].split(" ")[0]  # Récupérer uniquement le nom de l'emplacement

            # Récupérer l'objet Emplacement
            nouvel_emplacement_obj = self.controller.entrepots[nouvel_entrepot_selectionne].get_emplacement(nouvel_emplacement_nom)

            # Vérifier si le nouvel emplacement est vide
            if nouvel_emplacement_obj and nouvel_emplacement_obj.est_vide():
                confirmation = messagebox.askyesno(
                    "Confirmation",
                    f"Voulez-vous déplacer le produit {self.produit_selectionne.nom} de {self.entrepot_selectionne}/{self.emplacement_selectionne.nom} à {nouvel_entrepot_selectionne}/{nouvel_emplacement_obj.nom} ?"
                )
                if confirmation:
                    if self.controller.deplacer_produit(
                        self.entrepot_selectionne, self.emplacement_selectionne,
                        nouvel_entrepot_selectionne, nouvel_emplacement_obj
                    ):
                        messagebox.showinfo("Succès", f"Produit {self.produit_selectionne.nom} déplacé avec succès.")
                        self.popup.destroy()
                        self.afficher_arborescence()
                    else:
                        messagebox.showerror("Erreur", "Échec du déplacement du produit. Vérifiez que les emplacements sont corrects.")
                else:
                    self.popup.destroy()



    def afficher_arborescence(self):
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

if __name__ == "__main__":
    root = tk.Tk()
    controller = Controller()
    app = View(root, controller)
    root.mainloop()
