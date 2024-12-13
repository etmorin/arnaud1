from PIL import Image, ImageDraw, ImageFont
import os

def generate_bon_entree(entrepot_name, client_name, address, contact_name, contact_phone, ref_num, description, date_entree,lieu_CP, lieu_adresse, lieu_nom):
    # Vérifier si date_entree est un objet datetime et le convertir en chaîne si nécessaire
    if not isinstance(date_entree, str):
        date_entree = date_entree.strftime('%d/%m/%Y')  # Convertir en chaîne de caractères formatée

    # Créer une image blanche
    width, height = 800, 1000  # Dimensions de l'image
    image = Image.new('RGB', (width, height), 'white')
    draw = ImageDraw.Draw(image)

    # Charger une police plus appropriée si nécessaire
    try:
        font_bold = ImageFont.truetype("arialbd.ttf", 40)  # Police en gras pour le titre
        font = ImageFont.truetype("arial.ttf", 20)  # Police pour le reste du texte
    except IOError:
        font_bold = ImageFont.load_default()
        font = ImageFont.load_default()

    # Titre : Nom de l'entrepôt + Bon d'entrée
    title = f"{entrepot_name} / Bon d'entrée"
    title_bbox = draw.textbbox((0, 0), title, font=font_bold)
    draw.text(((width - (title_bbox[2] - title_bbox[0])) // 2, 50), title, font=font_bold, fill="black")

    # Référence BE + date + numéro du produit (sans 'prod-')
    ref_line = f"BE {date_entree.replace('/', '')}-{str(ref_num).replace('prod-', '')}"
    ref_line_bbox = draw.textbbox((0, 0), ref_line, font=font)
    draw.text(((width - (ref_line_bbox[2] - ref_line_bbox[0])) // 2, 110), ref_line, font=font, fill="black")

    # Client information
    draw.text((50, 200), "Client:", font=font_bold, fill="black")
    draw.text((50, 240), client_name or "Non disponible", font=font, fill="black")  # Valeur par défaut si None
    draw.text((50, 270), address or "Adresse non disponible", font=font, fill="black")  # Valeur par défaut si None

    # Contact information
    contact_text = f"Contact: {contact_name or 'Non disponible'} - {contact_phone or 'Numéro non disponible'}"
    draw.text((50, 320), contact_text, font=font, fill="black")

    #Lieu de chargement
    draw.text((380, 200), "Lieu de chargement:", font=font_bold, fill="black")
    draw.text((550, 240), f"Société :{lieu_nom}" or "Société:", font=font, fill="black")
    draw.text((550, 270), f"Adresse:{lieu_adresse}" or "Adresse:", font=font, fill="black")
    draw.text((550, 300), f"CP:{lieu_CP}" or "CP:", font=font, fill="black")

    # Date d'entrée
    draw.text(((width - (ref_line_bbox[2] - ref_line_bbox[0])) // 2, 130), f"Date d'entrée: {date_entree}", font=font, fill="black")

    # Colis et Description
    draw.text((50, 400), "Colis et Description:", font=font_bold, fill="black")
    draw.text((50, 440), f"Référence: {ref_num}", font=font, fill="black")
    draw.text((50, 470), f"Description: {description or 'Pas de description'}", font=font, fill="black")  # Valeur par défaut si None

    # Enregistrer le fichier comme image
    output_path = f"bon_entree_{ref_num}.png"
    image.save(output_path)
    return output_path

def generate_bon_sortie(entrepot_name, client_name, address, contact_name, contact_phone, ref_num, description, date_sortie):
    # Créer une image blanche
    width, height = 800, 1000
    image = Image.new('RGB', (width, height), 'white')
    draw = ImageDraw.Draw(image)

    # Police
    try:
        font_bold = ImageFont.truetype("arialbd.ttf", 40)
        font = ImageFont.truetype("arial.ttf", 20)
    except IOError:
        font_bold = ImageFont.load_default()
        font = ImageFont.load_default()

    # Titre : Nom de l'entrepôt + Bon de sortie
    title = f"{entrepot_name} / Bon de sortie"
    title_bbox = draw.textbbox((0, 0), title, font=font_bold)
    draw.text(((width - (title_bbox[2] - title_bbox[0])) // 2, 50), title, font=font_bold, fill="black")

    # Référence BS + date de sortie + numéro du produit (sans 'prod-')
    ref_line = f"BS {date_sortie.replace('/', '')}-{ref_num.replace('prod-', '')}"
    ref_line_bbox = draw.textbbox((0, 0), ref_line, font=font)
    draw.text(((width - (ref_line_bbox[2] - ref_line_bbox[0])) // 2, 110), ref_line, font=font, fill="black")

    # Client information
    draw.text((50, 200), "Client:", font=font_bold, fill="black")
    draw.text((50, 240), client_name, font=font, fill="black")
    draw.text((50, 270), address, font=font, fill="black")

    # Contact information
    contact_text = f"Contact: {contact_name} - {contact_phone or 'Numéro de téléphone non disponible'}"
    draw.text((50, 320), contact_text, font=font, fill="black")

    # Date de sortie (utilisation de l'attribut 'date_sortie')
    draw.text((550, 200), f"Date de sortie: {date_sortie}", font=font, fill="black")

    # Colis et Description
    draw.text((50, 400), "Colis et Description:", font=font_bold, fill="black")
    draw.text((50, 440), f"Référence: {ref_num}", font=font, fill="black")
    draw.text((50, 470), f"Description: {description}", font=font, fill="black")

    # Enregistrer le fichier comme image
    output_path = f"bon_sortie_{ref_num}.png"
    image.save(output_path)
    return output_path
