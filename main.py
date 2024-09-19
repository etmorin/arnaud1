# main.py

from controller import QRCodeController

def main():
    # Initialiser le contrôleur
    qr_controller = QRCodeController()

    while True:
        # Ajouter un produit via l'interaction
        qr_controller.ajouter_produit_interactif()

        # Demander à l'utilisateur s'il veut ajouter un autre produit
        continuer = input("Voulez-vous ajouter un autre produit ? (o/n) : ")
        if continuer.lower() != 'o':
            break

if __name__ == "__main__":
    main()
