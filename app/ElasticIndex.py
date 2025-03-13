from elasticsearch import Elasticsearch, ElasticsearchWarning
import time
import warnings

# Ignorer les avertissements Elasticsearch
warnings.filterwarnings("ignore", category=ElasticsearchWarning)

class ElasticIndex(object):
	"""doc ElasticIndex"""

	def __init__(self, url: str, index: str):
		self.es = Elasticsearch(url)
		self.index = index
		self.size_search = 0
		
		print(f"[*] Connexion au serveur Elasticsearch: {url}")

		if not self.es.ping():
			print(f"Connexion impossible avec Elasticsearch: {self.es.ping()}")
			exit(-1)

		# Vérifier si l'index existe déjà
		if not self.es.indices.exists(index=index):
		    # Définir la configuration de l'index
		    # (Improve the accuracy of substring searches, we use an analyzers and tokenizers to process the text in your documents)
			index_mapping = {
				"settings": {
					"index.max_ngram_diff": 14, 
					"analysis": {
			      		"tokenizer": {
				        	"ngram_tokenizer": {
				          		"type": "ngram",
				         		"min_gram": 2,
				         		"max_gram": 15,
				        		"token_chars": ["letter", "digit", "whitespace"]
				        	}
				      	},
				      	"analyzer": {
				        	"ngram_analyzer": {
				          		"type": "custom",
				          		"tokenizer": "ngram_tokenizer",
				          		"filter": ["lowercase"]
				        	}
					    }
				    }
				},
			    "mappings": {
			        "properties": {
			            "id": {
			                "type": "keyword"  # Champ id comme chaîne de caractères non analysée
			            },
			            "title": {
			                "type": "text",  # Champ titre avec analyse pour recherche textuelle
			                "analyzer": "ngram_analyzer"  # Utilisation de l'analyzer ngram ngram pour recherche partielle
			            },
			            "decision": {
			                "type": "keyword",
			            },
			            "path": {
			                "type": "keyword"
			            }
			        }
			    }
			}

		    # Créer l'index avec la configuration définie
			response = self.es.indices.create(index=index, body=index_mapping)
			print(f"Index créé: {response}")


	# Supprime tous les documents dans l'index
	def delete_all_data(self) -> None:
		response = self.es.delete_by_query(
		    index=self.index,
		    body={"query": {"match_all": {}}}
		)

		print(f"[*] Réinitialisation de l'index. \nNombre de documents supprimés : {response['deleted']}")

	# Envoyer les données juridiques vers un index
	def send_all_data(self, datas: str) -> None:
		print("[*] Envoie des données vers Elasticsearch...")
		for data in datas:
			data = {
				"id": data[0],
				"title": data[1],
				"decision": data[2],
				"path": data[3]
			}

			# Indexation
			response = self.es.index(index=self.index, document=data)
			# print(response)

	# Obtenir le nombre total de documents dans l'index
	def set_number_doc(self) -> None:
		self.size_search = self.es.count(index=self.index, body={"query": {"match_all": {}}})['count']
		print(f"[*] Nombre de documents dans l'index '{self.index}': {self.size_search}")

		
	# Trouver les valeurs uniques dans la colonne "décision"
	def get_unique_decision(self) -> list:
		response = self.es.search(
		    index=self.index,
			    body={
			    "size":0,
				"aggs" : {
				    "valeurs_uniques" : {
				        "terms" : {"field" : "decision", "size" : self.size_search}
				    }
				}
			}
		)

		# Renvoyer les valeurs uniques
		return sorted([bucket['key'] for bucket in response['aggregations']['valeurs_uniques']['buckets']])


	# Récupérer des textes filtrés par une décision
	def get_text_filter_by_decision(self, decision: str) -> str:
		return self.es.search(
		    index=self.index,
			    body={
			    "size": self.size_search if self.size_search <= 10000 else 10000,
				"query": {
					"wildcard": {
						"decision": { "value": decision }
					}
				}
			}
		)


if __name__ == '__main__':
	# Variables
	INDEX        = "juri_text" 
	URL          = "http://localhost:9200/"

	ei = ElasticIndex(URL, INDEX)
	# # Suppression de tous les documents pour ne pas avoir de doublons quand je relance le programme
	# ei.delete_all_data()

	# # Envoie de toutes les données contenues dans la liste
	# ei.send_all_data(datas)

	# # Temps d'attente pour que les données se chargent dans Elastic
	# time.sleep(1)
	# ei.set_number_doc()

	##############################

	# print(ei.get_unique_decision())
	# print(ei.get_text_filter_by_decision("ASSEMBLEE_PLENIERE"))
	# print(ei.get_text_filter_by_decision("AUCUNE"))

	
