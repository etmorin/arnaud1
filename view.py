# view.py

class QRCodeView:
    @staticmethod
    def imprimer_qr_code(produit):
        # Afficher les informations encodées dans le QR code
        print(f"---- QR Code Infos ----")
        print(f"Produit: {produit.nom}")
        print(f"ID généré: {produit.id}")
        print(f"QR code enregistré : {produit.qr_code}")
        print(f"-----------------------\n")
