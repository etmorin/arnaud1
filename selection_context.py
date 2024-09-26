from state import NeutralState

class SelectionContext:
    """
    Contexte pour gérer les états de sélection de produits.
    """
    def __init__(self, view, controller):
        self.state = NeutralState()
        self.view = view
        self.controller = controller  # Ajouter une référence au contrôleur

    def set_state(self, new_state):
        # Empêcher les transitions vers le même état
        if type(self.state) == type(new_state):
            return

        # Sortie de l'état actuel
        self.state.exit_state(self)

        # Changer d'état
        self.state = new_state

        # Entrer dans le nouvel état
        self.state.enter_state(self)

    def handle_selection(self, selected_item):
        # Vérifier si la réinitialisation est en cours dans la vue
        if self.view.resetting_selection:
            return

        # Gérer la sélection en fonction de l'état
        self.state.handle_selection(self, selected_item)

    def handle_action(self):
        self.state.handle_action(self)
