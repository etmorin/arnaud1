

# Ajouter tous les fichiers modifiés
git add .

# Supprimer les fichiers .env et .env.yaml de l'index (mais les laisser dans le répertoire de travail)
git rm --cached .env
git rm --cached .env.yaml

# Afficher un message de confirmation
Write-Host "Tous les fichiers ajoutés sauf .env et .env.yaml"
