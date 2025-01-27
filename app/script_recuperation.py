from ElasticIndex import ElasticIndex
from bs4 import BeautifulSoup
from lxml import etree
import requests
import os
import tarfile
import subprocess
import time

# Télécharger tous les fichiers tar.gz de l'url donnée
def downloading_files(url: str, path: str) -> list:
	print(f"[*] Début de la récupération des fichiers depuis l'URL '{url}' vers le dossier '{path}'.")

	response = requests.get(url)
	soup = BeautifulSoup(response.text, "html.parser")

	# Trouver tous les liens contenant les fichiers .tar.gz
	file_links = [
	    link.get("href") for link in soup.find_all("a", href=True) if link["href"].endswith(".tar.gz")
	]

	if not file_links:
		print("[!] Erreur: Aucun fichier sur l'url founit...")
		exit(-1)

	# print("[*] Fichiers trouvés :", file_links)


	# Dossier où le fichier sera enregistré
	os.makedirs(path, exist_ok=True)  # Créer le dossier s'il n'existe pas

	for file_link in file_links:
		# Vérification que le fichiers n'existe pas déjà
		output_path = os.path.join(path, file_link)

		if os.path.exists(output_path):
		    print(f"[!] Le fichier '{file_link}' existe déjà, téléchargement ignoré.")
		    continue

		print(f"Téléchargement du fichier: {file_link}")

		# Vérification de l'url et sauvegarde du fichier localement
		response = requests.get(url+file_link, stream=True)
		if response.status_code == 200:
			with open(path+file_link, 'wb') as f:
				f.write(response.raw.read())

	print(f"[*] Les fichiers ont été transférés avec succès dans le dossier '{path}'.")

	return file_links

# Extraire les fichiers tar.gz
def extracting_files(path: str, list_files: list) -> None:
	# Dossier où seront les fichiers extraient
	os.makedirs(path, exist_ok=True)

	print(f"[*] Extraction des fichiers tar.gz du dossier '{path}' vers le dossier '{path}'")

	for file_to_extract in list_files:
		with tarfile.open(path+file_to_extract, 'r:gz') as file:
		    file.extractall(path)  
		    print(f"Extraction réussie du fichier: {path+file_to_extract}")

	# Suppression des fichiers compressés
	os.system(f"rm {path}*.tar.gz")


# Récupérer le chemin de chaque fichier xml (avec la commande find)
def list_of_xml_files(path_source: str) -> list:
	print("[*] Récuperation des informations dans les fichiers xml...")

	command = ["find", path_source, "-type", "f", "-name", "*.xml"]

	# Exécuter la commande find pour récuperer chaque chemin des fichiers xml
	result = subprocess.run(command, stdout=subprocess.PIPE, text=True)

	# Récupérer les fichiers trouvés dans une liste (chaque ligne représente un fichier)
	path_xml_files = result.stdout.splitlines()

	# Afficher la liste des chemins des fichiers
	# print(len(path_xml_files))
	# print("\n".join(path_xml_files))

	return path_xml_files

# Récupérer l'id, le titre et la décision contenu dans un fichier xml
def get_xml_info(path_xml_file: list) -> tuple:
	# print(f"[*] Récuperation des infos du fichiers: {path_xml_file}")
	
	# Charger le fichier XML
	tree = etree.parse(path_xml_file)

	# Utiliser XPath pour trouver et extraire le texte
	info_id                   = tree.xpath('/TEXTE_JURI_JUDI/META/META_COMMUN/ID/text()')[0] 
	info_title                = tree.xpath('/TEXTE_JURI_JUDI/META/META_SPEC/META_JURI/TITRE/text()')[0] 
	info_decision_par_chambre = tree.xpath('/TEXTE_JURI_JUDI/META/META_SPEC/META_JURI_JUDI/FORMATION/text()')

	# Si un document n'a pas de décision par chambre
	if len(info_decision_par_chambre) == 0:
		info_decision_par_chambre = "AUCUNE"
	else:
		info_decision_par_chambre = info_decision_par_chambre[0]

	return (info_id, info_title, info_decision_par_chambre, path_xml_file)


if __name__ == '__main__':
	# Variables
	URL_FILES     = "https://echanges.dila.gouv.fr/OPENDATA/CASS/"
	PATH_OUTPUT   = f"{os.getcwd()}/documents/"

	URL_ELASTIC   = "http://host.docker.internal:9200/"
	INDEX_ELASTIC = "juri_text" 
	

	# Téléchargement des fichiers et extractions
	list_files = downloading_files(URL_FILES, PATH_OUTPUT)
	extracting_files(PATH_OUTPUT, list_files)

	# Récuperation du chemin des fichiers xml
	path_xml_files = list_of_xml_files(PATH_OUTPUT)

	# Les données des fichiers juridiques sont stockés dans une liste
	# Chaque élément est un tuple: (id, titre, décision et chemin vers le fichier xml)
	list_tuple_infos_juritext = [get_xml_info(path) for path in path_xml_files]

	# Connexion avec Elasticsearch
	ei = ElasticIndex(URL_ELASTIC, INDEX_ELASTIC)
	# Suppression de tous les documents pour ne pas avoir de doublons quand je relance le programme
	ei.delete_all_data()

	# Envoie de toutes les données contenues dans la liste
	ei.send_all_data(list_tuple_infos_juritext)

	print("[*] Extraction des documents et indexation dans Elasticsearch réussi!")

	##############################

	# # Temps d'attente pour que les données se chargent dans Elastic
	# time.sleep(1)
	# ei.set_number_doc()

	# print(ei.get_unique_decision())
	# print(ei.get_text_filter_by_decision("ASSEMBLEE_PLENIERE"))
	# print(ei.get_text_filter_by_decision("AUCUNE"))

