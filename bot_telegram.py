import requests
import feedparser
from datetime import datetime, timedelta

# --- CONFIGURATION ---
TOKEN = "8547065074:AAEiZ4Jw5maZMbkYAIiJtnrIMPv1hk5dU54"

# Ta liste avec ton ID et celui de Léa
LISTE_ID = ["6773491313", "7776912126"]

SOURCES = {
    "3Dnatives (FR)": "https://www.3dnatives.com/feed/",
    "3DPrint.com (USA)": "https://3dprint.com/feed/",
    "Thingiverse": "https://www.thingiverse.com/rss/newest",
    "Instructables": "https://www.instructables.com/rss/workshop/",
    "Hackaday": "https://hackaday.com/blog/category/3d-printing/feed/",
    "Engineering.com": "https://www.engineering.com/DesktopModules/Services/API/News/GetRss?category=Design%20Software",
    "All3DP": "https://all3dp.com/feed/",
    "Cults3D": "https://cults3d.com/fr/flux-de-conception.rss"
}

def envoyer_telegram(message):
    for chat_id in LISTE_ID:
        url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
        payload = {"chat_id": chat_id, "text": message, "parse_mode": "Markdown"}
        try:
            requests.post(url, data=payload)
        except Exception as e:
            print(f"Erreur d'envoi pour {chat_id}: {e}")

# ... (garde la suite du code avec compiler_actus_3d) ...

def compiler_actus_3d():
    print("Vérification des actus...")
    message_global = "🤖 *RÉCAP IMPRESSION 3D & CULTS*\n\n"
    il_y_a_24h = datetime.now() - timedelta(hours=24)
    trouve = False

    for nom_site, url_rss in SOURCES.items():
        flux = feedparser.parse(url_rss)
        for article in flux.entries[:3]:
            # Gestion de la date
            date_tuple = article.published_parsed if hasattr(article, 'published_parsed') else article.updated_parsed
            date_article = datetime(*date_tuple[:6])
            
            if date_article > il_y_a_24h:
                trouve = True
                message_global += f"📍 *{nom_site}*\n"
                message_global += f"👉 {article.title}\n"
                message_global += f"[Lien]({article.link})\n\n"

    if trouve:
        envoyer_telegram(message_global)
    else:
        envoyer_telegram("☕ Rien de neuf aujourd'hui, David.")

if __name__ == "__main__":
    compiler_actus_3d()




