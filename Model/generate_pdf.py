from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from datetime import datetime
import os

def ensure_directory_exists(directory_path):
    """
    Crée un dossier s'il n'existe pas déjà.
    """
    if not os.path.exists(directory_path):
        os.makedirs(directory_path)

def generate_bon_entree(produits, entrepot, controller, output_folder="bons_entree"):
    """
    Génère un bon d'entrée pour les produits sélectionnés en récupérant les informations des clients depuis Firebase.
    """
    ensure_directory_exists(output_folder)

    file_name = f"bon_entree_{datetime.now().strftime('%Y%m%d%H%M%S')}.pdf"
    output_path = os.path.join(output_folder, file_name)

    c = canvas.Canvas(output_path, pagesize=A4)
    width, height = A4

    # En-tête
    c.setFont("Helvetica-Bold", 14)
    c.drawString(50, height - 50, f"Arnaud Entrepôts")
    c.drawString(50, height - 70, f"Entrepôt: {entrepot}")
    c.drawString(50, height - 90, f"Date d'impression: {datetime.now().strftime('%d/%m/%Y %H:%M')}")
    c.line(50, height - 100, width - 50, height - 100)

    # Corps
    c.setFont("Helvetica", 12)
    y_position = height - 140

    for produit in produits:
        # Récupérer les données du client depuis Firebase
        client_data = controller.recuperer_data_client(produit.client)

        # Informations produit et client
        c.setFont("Helvetica-Bold", 12)
        c.drawString(50, y_position, f"Produit: {produit.nom}")
        y_position -= 20
        c.setFont("Helvetica", 12)
        c.drawString(50, y_position, f"Numéro de facture: {produit.id.replace('prod-', '')}")
        y_position -= 20
        c.drawString(50, y_position, f"Client: {client_data['nom']}")
        y_position -= 20
        c.drawString(50, y_position, f"Nom de Société: {client_data['nom_societe']}")
        y_position -= 20
        c.drawString(50, y_position, f"Adresse: {client_data['adresse']}")
        y_position -= 20
        c.drawString(50, y_position, f"Description: {produit.description}")
        y_position -= 20
        c.drawString(50, y_position, f"Date d'entrée: {produit.date_entree}")
        y_position -= 40
        c.line(50, y_position, width - 50, y_position)
        y_position -= 20

        if y_position < 100:
            c.showPage()
            y_position = height - 50

    # Sauvegarder le PDF
    c.save()
    return output_path

def generate_bon_sortie(produits, entrepot, client_data, output_dir="bons_sortie"):
    """
    Génère un bon de sortie au format PDF pour une liste de produits.
    """
    from reportlab.lib.pagesizes import A4
    from reportlab.pdfgen import canvas
    import os
    from datetime import datetime

    # Création du dossier de sortie
    os.makedirs(output_dir, exist_ok=True)

    # Chemin de sortie du fichier PDF
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    output_path = os.path.join(output_dir, f"bon_sortie_{timestamp}.pdf")

    # Initialisation du PDF
    c = canvas.Canvas(output_path, pagesize=A4)
    width, height = A4

    # En-tête
    c.setFont("Helvetica-Bold", 14)
    c.drawString(50, height - 50, "Arnaud Entrepôts")
    c.drawString(50, height - 70, f"Entrepôt : {entrepot}")
    c.drawString(50, height - 90, f"Date d'impression : {datetime.now().strftime('%d/%m/%Y %H:%M')}")

    # Client
    c.drawString(50, height - 120, "Client :")
    c.drawString(100, height - 140, f"Nom: {client_data['nom']}")
    c.drawString(100, height - 160, f"Société: {client_data['nom_societe']}")
    c.drawString(100, height - 180, f"Adresse: {client_data['adresse']}")

    # Ligne de séparation
    c.line(50, height - 190, width - 50, height - 190)

    # Corps
    c.setFont("Helvetica", 12)
    y_position = height - 220

    for produit in produits:
        facture_num = f"{datetime.now().strftime('%Y%m%d')}{produit.id.replace('prod-', '')}"
        c.drawString(50, y_position, f"Numéro de facture : {facture_num}")
        y_position -= 20
        c.drawString(50, y_position, f"Nom : {produit.nom}")
        y_position -= 20
        c.drawString(50, y_position, f"Description : {produit.description}")
        y_position -= 20
        c.drawString(50, y_position, f"Date d'entrée : {produit.date_entree}")
        y_position -= 40

        # Ajouter une nouvelle page si l'espace est insuffisant
        if y_position < 100:
            c.showPage()
            y_position = height - 50

    # Sauvegarde du fichier
    c.save()
    return output_path

