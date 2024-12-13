import os
import json
from dotenv import load_dotenv
import firebase_admin
from firebase_admin import credentials, db

# Charger le fichier .env
load_dotenv()

# Charger les informations d'identification depuis les variables d'environnement
firebase_credentials_json = os.getenv('FIREBASE_CREDENTIALS_JSON')

if not firebase_credentials_json:
    raise ValueError("La variable d'environnement FIREBASE_CREDENTIALS_JSON n'est pas définie.")

# Convertir le JSON en dictionnaire
firebase_credentials = json.loads(firebase_credentials_json)

# Initialiser l'application Firebase avec les informations d'identification
cred = credentials.Certificate(firebase_credentials)
firebase_admin.initialize_app(cred, {
    'databaseURL': 'https://programme-arnaud-default-rtdb.europe-west1.firebasedatabase.app/'  # Utilise l'URL correcte
})

# Définir la référence 'db' à partir de firebase_admin
db = firebase_admin.db
