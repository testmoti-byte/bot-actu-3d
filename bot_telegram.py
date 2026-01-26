import requests
import feedparser
from datetime import datetime, timedelta

# --- CONFIG ---
TOKEN = "8547065074:AAEiZ4Jw5maZMbkYAIiJtnrIMPv1hk5dU54"

# Ajoute l'ID de Léa ici dès que tu l'as (ex: "12345678")
LISTE_ID = ["6773491313", "7776912126"]

def envoyer_telegram(message):
    for chat_id in LISTE_ID:
        url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
        payload = {"chat_id": chat_id, "text": message, "parse_mode": "Markdown"}
        try:
            requests.post(url, data=payload)
        except Exception as e:
            print(f"Erreur d'envoi pour {chat_id}: {e}")

# --- LE RESTE DU CODE (SOURCES, COMPILER_ACTUS_3D, etc.) ---

SOURCES = {
    "3Dnatives (FR)": "https://www.3dnatives.com/feed/",
    "All3DP": "https://all3dp.com/feed/",
    "3D Printing Industry": "https://3dprintingindustry.com/feed/",
    "Cults3D (Nouveautés)": "https://cults3d.com/fr/flux-de-conception.rss",
    "Prusa Printers": "https://www.printables.com/en/rss/newest"
}

def envoyer_telegram(message):
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    payload = {"chat_id": CHAT_ID, "text": message, "parse_mode": "Markdown", "disable_web_page_preview": False}
    try:
        requests.post(url, data=payload)
    except Exception as e:
        print(f"Erreur d'envoi : {e}")

def compiler_actus_3d():
    print("Vérification des sites 3D...")
    message_global = "🤖 *RÉCAP IMPRESSION 3D & CULTS*\n\n"
    il_y_a_24h = datetime.now() - timedelta(hours=24)
    trouve = False

    for nom_site, url_rss in SOURCES.items():
        flux = feedparser.parse(url_rss)
        for article in flux.entries[:5]: # On regarde les 5 derniers de chaque site
            # Extraction de la date (gestion des formats différents)
            date_tuple = article.published_parsed if hasattr(article, 'published_parsed') else article.updated_parsed
            date_article = datetime(*date_tuple[:6])
            
            if date_article > il_y_a_24h:
                trouve = True
                message_global += f"📍 *{nom_site}*\n"
                message_global += f"👉 {article.title}\n"
                message_global += f"[Lien vers l'actu/modèle]({article.link})\n\n"

    if trouve:
        envoyer_telegram(message_global)
    else:
        envoyer_telegram("☕ Rien de neuf dans le monde de la 3D ces dernières 24h, David.")

if __name__ == "__main__":

    compiler_actus_3d()



