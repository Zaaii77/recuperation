from bs4 import BeautifulSoup
import pandas as pd
import asyncio
from datetime import datetime
from telegram import Bot

TELEGRAM_BOT_TOKEN = '6815472586:AAGC9qxCl2oJT5Mw-m6Gch97t0WcsGjvCX8'
TELEGRAM_CHANNEL_ID = '@evalyon'

# Charger le fichier HTML
with open('mvp_perdant.html', 'r', encoding='utf-8') as file:
    content = file.read()

# Analyser le HTML avec BeautifulSoup
soup = BeautifulSoup(content, 'html.parser')

# Extraire les tables avec la classe spécifique
tables = soup.find_all('table', class_='table table-borderless')

# Vérifier le nombre de tables trouvées
if len(tables) == 2:
    data_section1 = []
    data_section2 = []

    # Extraire les données de la première table
    for row in tables[0].find_all('tr'):
        cols = [col.text.strip() for col in row.find_all('td')]
        if cols:
            data_section1.append(cols)

    # Extraire les données de la deuxième table
    for row in tables[1].find_all('tr'):
        cols = [col.text.strip() for col in row.find_all('td')]
        if cols:
            data_section2.append(cols)

    # Créer deux tableaux avec pandas
    df_section1 = pd.DataFrame(data_section1, columns=['Joueur', 'K/D/A', 'Score'])
    df_section2 = pd.DataFrame(data_section2, columns=['Joueur', 'K/D/A', 'Score'])

    # Fragmenter la colonne 'K/D/A' en trois colonnes distinctes pour df_section1
    df_section1[['Kills', 'Deaths', 'Assists']] = df_section1['K/D/A'].str.split('/', expand=True)
    df_section1 = df_section1.drop(columns=['K/D/A'])

    # Fragmenter la colonne 'K/D/A' en trois colonnes distinctes pour df_section2
    df_section2[['Kills', 'Deaths', 'Assists']] = df_section2['K/D/A'].str.split('/', expand=True)
    df_section2 = df_section2.drop(columns=['K/D/A'])

    # Inverser les colonnes 'Joueur' et 'Score' pour df_section2
    df_section2[['Joueur', 'Score']] = df_section2[['Score', 'Joueur']]

    # Enregistrer les tableaux dans des fichiers CSV avec des noms spécifiques (utilisation du timestamp)
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    filename_section1 = f'{timestamp}.1.csv'
    filename_section2 = f'{timestamp}.2.csv'
    df_section1.to_csv(filename_section1, index=False)
    df_section2.to_csv(filename_section2, index=False)

    # Trouver le joueur avec le score le plus élevé dans chaque section
    joueur_max_score_section1 = df_section1.loc[df_section1['Score'].idxmax()]['Joueur']
    max_score_section1 = df_section1['Score'].max()

    joueur_max_score_section2 = df_section2.loc[df_section2['Score'].idxmax()]['Joueur']
    max_score_section2 = df_section2['Score'].max()

    # Comparer les scores des deux sections et enregistrer le joueur avec le score le plus élevé dans une variable
    if max_score_section1 > max_score_section2:
        joueur_max_score_global = joueur_max_score_section1
        max_score_global = max_score_section1
        section_gagnante = "Section 1"
    else:
        joueur_max_score_global = joueur_max_score_section2
        max_score_global = max_score_section2
        section_gagnante = "Section 2"

    print(f"\nLe joueur avec le score le plus élevé est {joueur_max_score_global} avec un score de {max_score_global}.")
    print(f"Cela provient de la {section_gagnante}.")

    # Envoyer le message au canal Telegram de manière asynchrone
    async def send_telegram_message():
        bot = Bot(token=TELEGRAM_BOT_TOKEN)
        message = f"Le MVP est {joueur_max_score_global}."
        await bot.send_message(chat_id=TELEGRAM_CHANNEL_ID, text=message, parse_mode='Markdown')

    # Exécuter la fonction asynchrone pour envoyer le message au canal Telegram
    import asyncio
    loop = asyncio.get_event_loop()
    loop.run_until_complete(send_telegram_message())

else:
    print("Erreur : Deux tables avec la classe spécifique n'ont pas été trouvées.")
