import subprocess
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup
import time
import hashlib
import multiprocessing
import asyncio
from bs4 import BeautifulSoup
import pandas as pd
from telegram import Bot

async def send_telegram_message(TELEGRAM_BOT_TOKEN, TELEGRAM_CHANNEL_ID, message):
    bot = Bot(token=TELEGRAM_BOT_TOKEN)
    await bot.send_message(chat_id=TELEGRAM_CHANNEL_ID, text=message, parse_mode='Markdown')

def run_table_script():
    try:
        # Charger le contenu HTML depuis le fichier index.html
        with open('index.html', 'r', encoding='utf-8') as file:
            content = file.read()

        # Analyser le HTML avec BeautifulSoup
        soup = BeautifulSoup(content, 'html.parser')

        # Vérifier si la div spécifique existe
        specific_div = soup.find('div', class_='display-2 lh-1 ff-gotham-bold text-uppercase')
        if specific_div:
            # Extraire le premier tableau
            table1 = soup.find_all('table', class_='table table-borderless')[0]  # Le premier tableau
            if table1:
                # Extraire les données du premier tableau
                data1 = []
                for row in table1.find_all('tr'):
                    cols = [col.text.strip() for col in row.find_all(['td', 'th'])]
                    data1.append(cols)

                # Créer un DataFrame pandas à partir des données du premier tableau
                df1 = pd.DataFrame(data1)

            # Extraire le deuxième tableau
            table2 = soup.find_all('table', class_='table table-borderless')[1]  # Le deuxième tableau
            if table2:
                # Extraire les données du deuxième tableau
                data2 = []
                for row in table2.find_all('tr'):
                    cols = [col.text.strip() for col in row.find_all(['td', 'th'])]
                    data2.append(cols)

                # Créer un DataFrame pandas à partir des données du deuxième tableau
                df2 = pd.DataFrame(data2)

                # Aligner les colonnes du deuxième tableau avec celles du premier tableau
                if len(df2.columns) > len(df1.columns):
                    df2 = df2.iloc[:, :len(df1.columns)]
                
                # Concaténer les deux DataFrames en un seul, en évitant la répétition des en-têtes
                merged_df = pd.concat([df1, df2], ignore_index=True)

                # Enregistrer le tableau fusionné dans un fichier CSV sans les en-têtes et les indices de colonnes
                merged_df.to_csv('tableau_fusionne.csv', index=False, header=False)
                print("Tableau fusionné enregistré avec succès dans tableau_fusionne.csv")

                # Trouver le pseudo du joueur avec le plus gros score
                numeric_rows = merged_df[merged_df.applymap(lambda x: x.isnumeric() if isinstance(x, str) else False).any(axis=1)]
                if not numeric_rows.empty:
                    max_score_row = numeric_rows[numeric_rows.iloc[:, 2].astype(int).idxmax()]
                    joueur_max_score = max_score_row.iloc[0]
                    max_score = max_score_row.iloc[2]

                    # Envoyer le message au canal Telegram de manière asynchrone
                    TELEGRAM_BOT_TOKEN = '6815472586:AAGC9qxCl2oJT5Mw-m6Gch97t0WcsGjvCX8'
                    TELEGRAM_CHANNEL_ID = '@evalyon'

                    loop = asyncio.new_event_loop()
                    asyncio.set_event_loop(loop)

                    loop.run_until_complete(send_telegram_message(TELEGRAM_BOT_TOKEN, TELEGRAM_CHANNEL_ID, f"Le joueur avec le plus gros score est {joueur_max_score} avec un score de {max_score}."))

                else:
                    print("Erreur : Aucune donnée numérique trouvée dans les tableaux.")
            else:
                print("Erreur : Deuxième tableau non trouvé.")
        else:
            print("Erreur : Div spécifique non trouvée.")

    except Exception as e:
        print(f"Une exception s'est produite : {e}")
        raise  # Relever l'exception pour redémarrer le script

async def main():
    url = 'https://tv.eva.gg/game-histories?locationId=14'
    chrome_options = Options()
    chrome_options.add_argument('--headless')
    chrome_options.add_argument('--log-level=3')

    while True:
        try:
            # Initialisation du navigateur
            driver = webdriver.Chrome(options=chrome_options)
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
                    tabl_process = multiprocessing.Process(target=run_table_script)
                    tabl_process.start()

        except Exception as e:
            print(f"Une exception s'est produite : {e}")

        finally:
            # Assurez-vous de fermer correctement le navigateur, même en cas d'exception
            driver.quit()

if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
