import os
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib import colors
from reportlab.platypus import Table, TableStyle
from datetime import date

def generer_bon_sortie(produits ,entrepot):
    # Initialiser le canvas
    c = canvas.Canvas(f"bon_sortie_{produits[0].date_depart}", pagesize=A4)
    largeur, hauteur = A4

    # En-tête
    c.setFont("Helvetica-Bold", 14)
    c.drawString(50, hauteur - 50, f"Bon de Sortie - Arnaud Entrepot")
    c.setFont("Helvetica", 10)
    c.drawString(50, hauteur - 70, f"Date : {date.today()}")