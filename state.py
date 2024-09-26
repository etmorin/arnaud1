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
    """
    État neutre : aucune action spécifique en cours.
    """
    def handle_selection(self, context, selected_item):
        # Gérer la sélection d'un élément dans l'état neutre
        if context.view.is_product_selected(selected_item):
            context.set_state(ProductSelectedState())
            context.view.update_interface_for_selection(selected_item)
        else:
            context.view.reset_selection()

    def handle_action(self, context):
        # Aucune action spécifique en état neutre
        pass

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
        # Changer de sélection : revenir à l'état neutre si la sélection change
        context.set_state(NeutralState())
        context.handle_selection(selected_item)

    def handle_action(self, context):
        # Sauvegarder l'emplacement de départ avant de passer en MovingProductState
        context.view.emplacement_depart = {
            'entrepot': context.view.entrepot_selectionne,
            'emplacement': context.view.emplacement_selectionne,
            'objet_emplacement': context.controller.entrepots[context.view.entrepot_selectionne].get_emplacement(context.view.emplacement_selectionne)
        }
        print(f"Emplacement de départ sauvegardé : {context.view.emplacement_depart['emplacement']} dans {context.view.emplacement_depart['entrepot']}")

        # Activer le mode de déplacement
        context.set_state(MovingProductState())
        context.view.activate_move_mode()

    def enter_state(self, context):
        print("Entrée dans l'état ProductSelectedState.")
        context.view.update_interface_for_product_selected()

    def exit_state(self, context):
        print("Sortie de l'état ProductSelectedState.")

class MovingProductState(State):
    """
    État où le produit est en cours de déplacement.
    """
    def handle_selection(self, context, selected_item):
        # Retirer la vérification de l'emplacement vide
        # Vérifier que l'emplacement de départ est bien sauvegardé dans la Vue
        if context.view.emplacement_depart:
            # Clic pour sélectionner la destination
            context.view.confirm_move(selected_item)
            context.set_state(NeutralState())
        else:
            print("Erreur : Emplacement de départ non défini dans la Vue.")
    
    def handle_action(self, context):
        # Pas d'autre action possible pendant le déplacement
        pass

    def enter_state(self, context):
        print("Entrée dans l'état MovingProductState.")
        context.view.update_interface_for_moving_product()

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
