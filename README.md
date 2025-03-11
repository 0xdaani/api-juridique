# Test technique Juri'Predis 2025

## Description

Ce projet est conçu pour collecter, traiter et mettre à disposition des données juridiques (décisions de la cour de cassation) via une API REST.  
Il repose sur **Python**, **FastAPI**, **Elasticsearch**, et **Docker**.  
L'objectif principal est de faciliter l'accès aux décisions juridiques, soit via une exploration structurée, soit par une recherche par mots-clés. 

---

## Fonctionnalités

### 1. Collecte et Indexation des Données

Ce script assure le traitement des données :  
1.	Récupération des données : Télécharge les fichiers depuis l’URL https://echanges.dila.gouv.fr/OPENDATA/CASS/ et les stocke dans le dossier `documents/`.  
2.	Extraction : Décompresse les archives tar.gz dans le même dossier.  
3.	Connexion à **Elasticsearch** : Établit une connexion avec un cluster Elasticsearch situé à http://localhost:9200/ sur l’index nommé `juri_text`.  
4.	Envoi des données : Envoie les données structurées (champs : `id`, `title`, `decision`, `path`) vers l’index Elasticsearch.  

Une fois les données indexées, le programme termine son exécution.

### 2. Serveur API avec FastAPI

Le deuxième script lance un serveur **FastAPI** permettant de consommer les données juridiques au format JSON. Deux modes d'accès aux données sont disponibles :

1. **Navigation structurée** : 
   - Sélectionner un type de décision.
   - Choisir un texte parmi les résultats associés.

2. **Recherche par titre** : 
   - Rechercher des données via le titre.

### 3. ElasticIndex.py

Cette classe est utilisée par `script_recuperation.py` et `app.py`. 
Elle est dédiée à la gestion des interactions avec Elasticsearch :
- Connexion à un index.
- Définition du mapping d’un index.
- Suppression de tous les documents présents dans un index.
- Envoi de nouvelles données vers Elasticsearch.
- Exécution de requêtes personnalisées.

---

## Usage

Prérequis: Installer Docker (avec Docker Compose).

```bash
git clone https://github.com/0xdaani/Test-techique-juripredis
cd Test-techique-juripredis/

# Démarrer Elasticsearch avec Docker Compose
docker-compose up elasticsearch

# Dans un autre terminal, construire l’image Docker pour l’application FastAPI. (Cela peut prendre 5-10 minutes)
docker build -t fastapi-app .

# Lancer le conteneur FastAPI
docker run --rm -p 8000:8000 fastapi-app

```

Se rendre sur http://127.0.0.1:8000/ pour accéder à l’API.

## Stopper les programmes

Appuyer sur CTRL+C pour stopper les programmes.

```bash
# Pour stopper le service Elasticsearch
docker-compose down
```

---

## Exemple de recherches

http://127.0.0.1:8000/search?query=14+avril

http://127.0.0.1:8000/search?query=14+avri




