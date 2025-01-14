from elasticsearch import Elasticsearch
import time


class ElasticIndex(object):
	"""doc ElasticIndex"""

	def __init__(self, url, index):
		self.es = Elasticsearch(url)
		self.index = index
		self.size_search = 0
		
		print(f"[*] Connexion au serveur Elasticsearch: ({url}{index})")

		# Vérifier si l'index existe déjà
		if not self.es.indices.exists(index=index):
		    # Définir la configuration de l'index (facultatif)
		    settings = {
		        "settings": {
		            "number_of_shards": 1,  # Nombre de partitions (shards)
		            "number_of_replicas": 1  # Nombre de réplicas
		        },
		        "mappings": {
		            "properties": {
			            "id": {"type": "keyword"},
			            "title": {"type": "text"},
			            "decision": {"type": "keyword"},
			            "path": {"type": "text"}
		            }
		        }
		    }

		    # Créer l'index avec la configuration définie
		    response = self.es.indices.create(index=index, body=settings)
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
	INDEX_ELASTIC        = "juri_text" 
	URL_ELASTIC          = "http://localhost:9200/"

	ei = ElasticIndex(URL_ELASTIC, INDEX_ELASTIC)
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

	