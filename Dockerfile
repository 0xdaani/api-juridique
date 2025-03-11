# Utiliser une image officielle de Python comme base
FROM python:3.9-slim

# Définir le répertoire de travail
WORKDIR /usr/src/app

# Installer les dépendances si nécessaire
COPY requirements.txt /usr/src/app/
RUN pip install --no-cache-dir -r requirements.txt

# Copier les fichiers dans le conteneur
COPY app/ /usr/src/app/

# Exécuter le script de récupération uniquement pendant le build
RUN python3 -u script_recuperation.py

# Exposer le port 8000 pour FastAPI
EXPOSE 8000

# Lancer le serveur fastAPI
CMD ["fastapi", "run", "app.py", "--port", "8000"]
