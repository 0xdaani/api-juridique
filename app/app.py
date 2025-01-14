from fastapi.responses import HTMLResponse, JSONResponse
from fastapi import FastAPI
from ElasticIndex import ElasticIndex
import requests
import json
from lxml import etree

ei = ElasticIndex("http://localhost:9200/", "juri_text")
ei.set_number_doc()

# Créer l'application FastAPI
app = FastAPI()


# Route pour la page principale
@app.get("/", response_class=HTMLResponse)
async def home():
    # Affichage de la page principale avec le choix du type de décision
    html_content = """
    <html>
        <head>
            <title>Test technique</title>
        </head>
        <body>
            <h1>Liste des décisions rendues par la cour de cassation</h1>
            
            <form action="/search" method="get">
                <input type="text" name="query" placeholder="Recherche un titre de document" required>
                <button type="submit">Rechercher</button>
            </form>
            
            <h2>Choisir le type de décision:</h2>

    """
    
    # Ajouter chaque élément à la page HTML
    for decision in ei.get_unique_decision():
        html_content += f"<a href='/decision?item={decision}'>{decision}</a><br>"

    html_content += """
        </body>
    </html>
    """

    return html_content


# Route pour afficher une liste de texte juridique (id - titre) en fonction du type de décision
@app.get("/decision", response_class=HTMLResponse)
async def show_value(item: str):
    liste_juri_text = ""
    for juri_text in ei.get_text_filter_by_decision(item)['hits']['hits']:
        liste_juri_text += f"<a href='/json-data?id={juri_text['_source']['id']}'>{juri_text['_source']['id']} - {juri_text['_source']['title']}</a><br/>"

    html_content = f"""
    <html>
        <head>
            <title>Test technique</title>
        </head>
        <body>
            <a href="/">Revenir à la page principale</a>
            <h1>Textes de juridictions filtrés par '{item}'</h1>
    """

    html_content += liste_juri_text
            
    html_content += """
        </body>
    </html>
    """

    return html_content


# Route pour renvoyer des données JSON
@app.get("/json-data", response_class=JSONResponse)
async def json_data(id: str):
    response = ei.es.search(index=ei.index, body={
        "query": {
            "term": {
                "id": {"value": id}
            }
        }
    })

    # Si l'id n'existe pas dans l'index Elastic
    if not response['hits']['hits']:
        data = {'data':'not found'}
    else:
        path = response['hits']['hits'][0]['_source']['path']
        # Charger le fichier XML
        tree = etree.parse(path)

        # Utiliser XPath pour trouver et extraire le texte
        info_title   = tree.xpath('/TEXTE_JURI_JUDI/META/META_SPEC/META_JURI/TITRE/text()')[0] 
        info_contenu = tree.xpath('/TEXTE_JURI_JUDI/TEXTE/BLOC_TEXTUEL/CONTENU/text()')

        # Exemple de données JSON
        data = {
            "id": id,
            "title": info_title,
            "content": info_contenu
        }

    return data


# Route pour gérer les résultats de recherche
@app.get("/search", response_class=HTMLResponse)
async def search(query: str):

    response = ei.es.search(index=ei.index, body={
        "query": {
            "match_phrase": {
                "title": f"{query}"
            }
        },
        "size":ei.size_search if ei.size_search <= 10000 else 10000
    })


    html_content = f"""
    <html>
        <head>
            <title>Test technique</title>
        </head>
        <body>
            <a href="/">Revenir à la page principale</a>
            <h1>Résultat de la recherche sur '{query}'</h1>
    """

    # Si la recherche sur le titre ne renvoie rien
    if not response['hits']['hits']:
        html_content += "Aucun résultat"
    else:
        # Trier les résultats de la recherche par la clé '_score' (le score de recherche)
        sorted_response = sorted(response['hits']['hits'], key=lambda element: element['_score'], reverse=True)

        for doc in sorted_response:
            html_content += f"<a href='/json-data?id={doc['_source']['id']}'>{doc['_source']['id']} - {doc['_source']['title']}</a><br/>"


    html_content += """
        </body>
    </html>
    """
    return html_content

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app:app", host="127.0.0.1", port=8000, reload=True)