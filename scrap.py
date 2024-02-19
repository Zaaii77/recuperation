import subprocess
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup
import time
import hashlib

url = 'https://tv.eva.gg/game-histories?locationId=14'
chrome_options = Options()
chrome_options.add_argument('--headless')
chrome_options.add_argument('--log-level=3')  # Définir le niveau de journalisation sur "info" ou "fatal"

driver = webdriver.Chrome(options=chrome_options)

driver.get(url)

# Attendez que la page soit complètement chargée
time.sleep(1)

# Récupérez le code source de la page après le chargement complet
html = driver.page_source

# Utilisez BeautifulSoup pour analyser le HTML
soup = BeautifulSoup(html, 'html.parser')

# Récupérez le contenu initial des div text-truncate
initial_content_hashes = [hashlib.sha256(str(element.text).encode('utf-8')).hexdigest() for element in soup.find_all('div', class_='text-truncate')]

# Générez un nom de fichier unique en utilisant le timestamp actuel
filename = 'index.html'

# Enregistrez le code source dans un fichier HTML pour la première itération
with open(filename, 'w', encoding='utf-8') as file:
    file.write(str(soup.prettify()))

try:
    # Récupérez le code source de la page après le chargement complet
    html = driver.page_source
    time.sleep(30)  # Attendez 30 secondes

    # Actualisez la page pour déclencher le chargement dynamique
    driver.refresh()

    # Attendez que la page soit complètement chargée après l'actualisation
    time.sleep(1)

    # Utilisez BeautifulSoup pour analyser le HTML
    soup = BeautifulSoup(html, 'html.parser')

    # Récupérez le nouveau contenu des div text-truncate
    new_content_hashes = [hashlib.sha256(str(element.text).encode('utf-8')).hexdigest() for element in soup.find_all('div', class_='text-truncate')]

    # Comparez les empreintes pour déterminer si le contenu a changé
    if new_content_hashes != initial_content_hashes:
        # Le contenu a changé ou c'est la première itération, enregistrez le code source dans le fichier index.html
        with open(filename, 'w', encoding='utf-8') as file:
            file.write(str(soup.prettify()))

        # Mettez à jour les empreintes pour le nouveau contenu
        initial_content_hashes = new_content_hashes

        # Lancer le script tabl.py
        subprocess.run(['python3', 'tabl.py'])
except KeyboardInterrupt:
    # Interrompre la boucle si l'utilisateur appuie sur Ctrl+C
    pass
finally:
    # Fermez le navigateur à la fin
    driver.quit()
