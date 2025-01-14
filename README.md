# Test technique Juri'predis 2025
## Ce qui a été fait

### Étape 1
- Récupérer et stocker les décisions de la cour de cassation.

### Étape 2: API REST
- Renvoyer une liste de toutes les décisions de cour de cassation (afficher uniquement l'identifiant et le titre de la décision)
Pouvoir filtrer les décisions par chambre (dans le document XML voir élément FORMATION: TEXTE_JURI_JUDI > META > META_SPEC > META_JURI_JUDI > FORMATION)
- Renvoyer le contenu d'une décision (identifiant, titre et contenu) en fonction d'un identifiant de décision
- L'API doit renvoyer les données en JSON
- Faire une recherche textuelle basique qui retourne les décisions correspondantes triées par score de pertinence


## Fonctionnement
### script_recuperation.py

Ce script assure le traitement des données :
- 1.	Récupération des données : Télécharge les fichiers depuis l’URL https://echanges.dila.gouv.fr/OPENDATA/CASS/ et les stocke dans le dossier `documents/`.
- 2.	Extraction : Décompresse les archives tar.gz dans le même dossier.
- 3.	Connexion à Elasticsearch : Établit une connexion avec un cluster Elasticsearch situé à http://localhost:9200/ sur l’index nommé `juri_text`.
- 4.	Envoi des données : Envoie les données structurées (champs : `id`, `title`, `decision`, `path`) vers l’index Elasticsearch.

Une fois les données indexées, le programme termine son exécution.

#### ElasticIndex.py

Cette classe est utilisée par `script_recuperation.py`. 
Elle est dédiée à la gestion des interactions avec Elasticsearch :
- Connexion à un index.
- Définition du mapping d’un index.
- Suppression de tous les documents présents dans un index.
- Envoi de nouvelles données vers Elasticsearch.
- Exécution de requêtes personnalisées.

### app.py

Ce script lance un serveur FastAPI pour fournir une API qui permet d’interagir avec les données des fichiers XML indexés dans Elasticsearch. Les principales routes disponibles sont :
- `/` : Recherche générique dans les données.
- `/decision` : Affiche les textes filtrés par la valeur du champ decision.
- `/json_data` : Retourne les données JSON associées à un fichier.
- `/search` : Fournit les résultats d’une recherche spécifique.


## Usage

```bash
docker-compose up

# Dans un autre terminal, une fois que Elasticsearch est prêt (aller sur l'url du serveur Elasticsearch http://localhost:9200/)
pip install -r requirements.txt
cd app/

# L'execution du fichier script_recuperation.py peut prendre quelques minutes (5-10 min)
python3 script_recuperation.py

# Ensuite lancer la commande et ce rendre sur cet url:
# http:localhost:8000
python3 app.py
```

Appuyer sur CTRL+C pour stopper les programmes.


## Exemple d'une recherche recherche

[](http://127.0.0.1:8000/search?query=1+avril)


## Améliorations Souhaitées

Voici les éléments que j’aurais aimé implémenter pour améliorer le projet :
- Recherche plus complète : Permettre une recherche non seulement sur le titre (`title`), mais aussi sur le contenu des documents.
- Résultats étendus : Configurer Elasticsearch pour que les recherches retournent plus de 10 000 documents, en dépassant la limite par défaut.
- Recherche partielle : Implémenter une recherche fonctionnelle sur des mots partiellement écrits. Exemple: la recherche sur le terme '14 avri' pour '14 avril' ne renvoie rien.
- Création d’un Dockerfile : Ajouter un fichier Dockerfile pour conteneuriser l’application et faciliter son déploiement.
- Stockage dans une base de données : Ajouter une base de données pour centraliser les champs `id`, `title`, `decision` et `contenu`.


