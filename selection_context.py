from state import NeutralState, ProductSelectedState, MovingProductState

class SelectionContext:
    """
    Contexte pour gérer les états de sélection de produits.
    """
    def __init__(self, view, controller):
        self.state = None  # Définit initialement l'état à None
        self.view = view
        self.controller = controller

    def set_state(self, new_state):
        # Empêcher les transitions vers le même état
        if type(self.state) == type(new_state):
            return

        if self.state:
            self.state.exit_state(self)

        # Changer d'état
        self.state = new_state

        # Entrer dans le nouvel état
        self.state.enter_state(self)

    def handle_selection(self, selected_item):
        """
        Gère la sélection dans l'arborescence en fonction de l'état courant.
        """
        # Si on est dans MovingProductState, ne pas immédiatement retourner à NeutralState
        if isinstance(self.state, MovingProductState):
            if self.view.is_empty_location(selected_item):
                print("MovingProductState : Emplacement vide sélectionné, déplacer le produit.")
                self.view.confirm_move(selected_item)  # Déplacer le produit
                self.set_state(NeutralState())  # Revenir à NeutralState après le déplacement
            else:
                # Si l'emplacement n'est pas vide, proposer un échange
                produit_cible = self.view.get_produit_at(selected_item)
                self.view.confirmer_echange(produit_cible, selected_item)
            return  # Terminer l'exécution ici pour éviter de retourner à NeutralState

        # Autres cas : on utilise la gestion normale des états (NeutralState, ProductSelectedState)
        if self.view.is_empty_location(selected_item):
            print("NeutralState : Emplacement vide sélectionné. On reste en NeutralState.")
            self.set_state(NeutralState())
        else:
            print("Produit sélectionné. Passage à ProductSelectedState.")
            self.set_state(ProductSelectedState())



    def handle_action(self):
        self.state.handle_action(self)
