import subprocess
from selenium import webdriver
from selenium.webdriver.firefox.options import Options as FirefoxOptions
from bs4 import BeautifulSoup
import time
import hashlib
import multiprocessing

def run_tabl_script():
    # Code de votre script tabl.py
    print("Le script tabl.py est en cours d'exécution.")

# Reste du code pour le scraping
url = 'https://tv.eva.gg/game-histories?locationId=14'

firefox_options = FirefoxOptions()
firefox_options.set_capability("moz:firefoxOptions", {"log": {"level": "trace", "file": "/chemin/vers/geckodriver.log"}})
firefox_options.headless = True

while True:
    try:
        # Initialisation du navigateur Firefox
        driver = webdriver.Firefox(options=firefox_options)
        driver.get(url)

        # Attendez que la page soit complètement chargée
        time.sleep(1)

        # Récupérez le code source de la page après le chargement complet
        html = driver.page_source

        # Utilisez BeautifulSoup pour analyser le HTML
        soup = BeautifulSoup(html, 'html.parser')

        # Récupérez le contenu initial de l'élément avec la classe spécifique
        initial_content = soup.find('div', class_='display-2 lh-1 ff-gotham-bold').text.strip()

        # Générez un nom de fichier unique en utilisant le timestamp actuel
        filename = 'index.html'

        # Enregistrez le code source dans un fichier HTML pour la première itération
        with open(filename, 'w', encoding='utf-8') as file:
            file.write(str(soup.prettify()))

        while True:
            # Actualisez la page pour déclencher le chargement dynamique
            driver.refresh()

            # Attendez que la page soit complètement chargée après l'actualisation
            time.sleep(3)

            # Récupérez le code source de la page après le chargement complet
            html = driver.page_source

            # Utilisez BeautifulSoup pour analyser le HTML
            soup = BeautifulSoup(html, 'html.parser')

            # Récupérez le nouveau contenu de l'élément avec la classe spécifique
            new_content = soup.find('div', class_='display-2 lh-1 ff-gotham-bold').text.strip()

            # Comparez les textes pour déterminer si le contenu a changé
            if new_content != initial_content:
                # Le contenu a changé, enregistrez le code source dans le fichier index.html
                with open(filename, 'w', encoding='utf-8') as file:
                    file.write(str(soup.prettify()))

                # Mettez à jour le contenu initial pour le nouveau contenu
                initial_content = new_content

                # Lancer le script tabl.py en tant que processus indépendant
                tabl_process = multiprocessing.Process(target=run_tabl_script)
                tabl_process.start()

    except KeyboardInterrupt:
        print("Arrêt du script suite à une interruption de l'utilisateur.")
        break
    finally:
        print("Fermeture du navigateur.")
        # Fermez le navigateur à la fin de chaque itération
        driver.quit()