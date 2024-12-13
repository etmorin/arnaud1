from abc import ABC, abstractmethod

class State(ABC):
    """
    Interface pour les états de sélection de produits.
    """

    @abstractmethod
    def handle_selection(self, context, selected_item):
        pass

    @abstractmethod
    def handle_action(self, context):
        pass

    @abstractmethod
    def enter_state(self, context):
        pass

    @abstractmethod
    def exit_state(self, context):
        pass

class NeutralState(State):
    def handle_selection(self, context, selected_item):
        if context.view.is_empty_location(selected_item):
            print("NeutralState : Emplacement vide sélectionné. On reste en NeutralState.")
        else:
            print("NeutralState : Produit sélectionné. Passage à ProductSelectedState.")
            context.set_state(ProductSelectedState())
            context.state.handle_selection(context, selected_item)

    def handle_action(self, context):
        # Pas d'action spécifique à cet état
        print("NeutralState : Aucune action à gérer dans cet état.")

    def enter_state(self, context):
        print("Entrée dans l'état neutre.")
        context.view.reset_interface()

    def exit_state(self, context):
        print("Sortie de l'état neutre.")

class ProductSelectedState(State):
    """
    État où un produit est sélectionné.
    """

    def handle_selection(self, context, selected_item):
        # On ne change pas d'état ici, on reste en ProductSelectedState
        if context.view.is_product_selected(selected_item):
            print("Produit sélectionné. Rester dans ProductSelectedState.")
        else:
            # Si l'utilisateur sélectionne un emplacement vide, revenir à l'état neutre
            context.set_state(NeutralState())

    def handle_action(self, context):
        # L'action "Déplacer Produit" déclenche le passage à MovingProductState
        print("Passage à MovingProductState.")
        context.set_state(MovingProductState())

    def enter_state(self, context):
        print("Entrée dans l'état ProductSelectedState.")
        context.view.update_interface_for_product_selected()

    def exit_state(self, context):
        print("Sortie de l'état ProductSelectedState.")

class MovingProductState(State):
    """
    État où un produit est en cours de déplacement.
    """

    def handle_selection(self, context, selected_item):
        """
        Gère la sélection du nouvel emplacement où le produit doit être déplacé.
        """
        if context.view.is_empty_location(selected_item):
            # Notifie la vue de déplacer le produit vers un emplacement vide
            print("Emplacement vide sélectionné. Déplacement du produit.")
            context.view.confirm_move(selected_item)  # Effectuer le déplacement du produit
            # Après le déplacement, on peut revenir à NeutralState
            context.set_state(NeutralState())
        else:
            # Demande à la vue de gérer l'échange avec confirmation
            produit_cible = context.view.get_produit_at(selected_item)  # Récupérer le produit à l'emplacement sélectionné
            context.view.confirmer_echange(produit_cible, selected_item)

    def handle_action(self, context):
        print("MovingProductState : Aucune action directe à ce stade.")

    def enter_state(self, context):
        print("Entrée dans l'état MovingProductState. Sélectionnez un emplacement pour déplacer le produit.")

    def exit_state(self, context):
        print("Sortie de l'état MovingProductState.")



class AddingProductState(State):
    """
    État où l'on ajoute un produit à un emplacement sélectionné.
    """
    def __init__(self):
        # Sauvegarder les informations sur l'emplacement et l'entrepôt sélectionnés
        self.entrepot_selectionne = None
        self.emplacement_selectionne = None

    def handle_selection(self, context, selected_item):
        # Aucune action de sélection pendant l'ajout de produit
        pass

    def handle_action(self, context):
        # Aucune autre action spécifique pendant l'ajout
        pass

    def enter_state(self, context):
        print("Entrée dans l'état AddingProductState.")
        # Sauvegarder les informations de l'emplacement et l'entrepôt sélectionnés
        self.entrepot_selectionne = context.view.entrepot_selectionne
        self.emplacement_selectionne = context.view.emplacement_selectionne
        # Ouvrir la fenêtre contextuelle pour l'ajout de produit
        context.view.ouvrir_fenetre_ajout_produit()

    def exit_state(self, context):
        print("Sortie de l'état AddingProductState.")

class ProductDisplayPhase:
    pass

class EditPhase:
    pass

class NothingSelectedState(State):
    """
    État où aucun produit ou emplacement n'est sélectionné.
    Désactive tous les boutons sauf "Ajouter Entrepôt" et "Ajouter Client".
    """

    def handle_selection(self, context, selected_item):
        # Aucun produit ou emplacement sélectionné, rester dans NothingSelectedState
        print("Rien n'est sélectionné. Aucune action possible.")
    
    def handle_action(self, context):
        # Désactiver toutes les actions dans cet état
        print("Aucune action possible dans l'état NothingSelected.")

    def enter_state(self, context):
        print("Entrée dans l'état NothingSelected.")
        context.view.update_interface_for_nothing_selected()

    def exit_state(self, context):
        print("Sortie de l'état NothingSelected.")
