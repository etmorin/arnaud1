from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from datetime import datetime

def generate_bon_entree(produits, entrepot, output_path=f"bon_entree_{datetime.now().strftime('%Y%m%d%H%M%S')}.pdf"):
    c = canvas.Canvas(output_path, pagesize=A4)
    width, height = A4

    # En-tête
    c.setFont("Helvetica-Bold", 14)
    c.drawString(50, height - 50, "Arnaud Entrepots")
    c.drawString(50, height - 70, f"Entrepôt: {entrepot}")
    c.drawString(50, height - 90, f"Date d'impression: {datetime.now().strftime('%d/%m/%Y %H:%M')}")

    # Ligne de séparation après l'en-tête
    c.line(50, height - 100, width - 50, height - 100)

    # Corps
    c.setFont("Helvetica", 12)
    y_position = height - 140

    for produit in produits:
        # Informations du produit
        facture_num = f"{datetime.now().strftime('%Y%m%d')}{produit.id.replace('prod-', '')}"
        c.drawString(50, y_position, f"Numéro de facture: {facture_num}")
        y_position -= 20
        c.drawString(50, y_position, f"Nom: {produit.nom}")
        y_position -= 20
        c.drawString(50, y_position, f"Description: {produit.description}")
        y_position -= 20
        c.drawString(50, y_position, f"Client: {produit.client.nom if produit.client else 'Non défini'}")
        y_position -= 20
        c.drawString(50, y_position, f"Date d'entrée: {produit.date_entree}")
        y_position -= 40

        # Ligne pointillée pour séparer les produits
        c.setDash(3, 3)
        c.line(50, y_position + 10, width - 50, y_position + 10)
        c.setDash()

        # Ajouter une nouvelle page si nécessaire
        if y_position < 100:
            c.showPage()
            y_position = height - 50

    # Sauvegarder le fichier
    c.save()
    return output_path

def generate_bon_sortie(produits, entrepot, client, output_path=f"bon_sortie_{datetime.now().strftime('%Y%m%d%H%M%S')}.pdf"):
    c = canvas.Canvas(output_path, pagesize=A4)
    width, height = A4

    # En-tête
    c.setFont("Helvetica-Bold", 14)
    c.drawString(50, height - 50, "Arnaud Entrepots")
    c.drawString(50, height - 70, f"Entrepôt: {entrepot}")
    c.drawString(50, height - 90, f"Client: {client.nom}")
    c.drawString(50, height - 110, f"Date d'impression: {datetime.now().strftime('%d/%m/%Y %H:%M')}")

    # Ligne de séparation après l'en-tête
    c.line(50, height - 120, width - 50, height - 120)

    # Corps
    c.setFont("Helvetica", 12)
    y_position = height - 160

    for produit in produits:
        # Informations du produit
        facture_num = f"{datetime.now().strftime('%Y%m%d')}{produit.id.replace('prod-', '')}"
        c.drawString(50, y_position, f"Numéro de facture: {facture_num}")
        y_position -= 20
        c.drawString(50, y_position, f"Nom: {produit.nom}")
        y_position -= 20
        c.drawString(50, y_position, f"Description: {produit.description}")
        y_position -= 20
        c.drawString(50, y_position, f"Date d'entrée: {produit.date_entree}")
        y_position -= 20
        c.drawString(50, y_position, f"Date de sortie: {datetime.now().strftime('%d/%m/%Y')}")
        y_position -= 40

        # Ligne pointillée pour séparer les produits
        c.setDash(3, 3)
        c.line(50, y_position + 10, width - 50, y_position + 10)
        c.setDash()

        # Ajouter une nouvelle page si nécessaire
        if y_position < 100:
            c.showPage()
            y_position = height - 50

    # Sauvegarder le fichier
    c.save()
    return output_path
