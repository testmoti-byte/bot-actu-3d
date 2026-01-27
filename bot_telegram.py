import requests
import feedparser
from datetime import datetime, timedelta
from deep_translator import GoogleTranslator

def traduire(texte):
    try:
        # Traduit n'importe quelle langue vers le Français
        return GoogleTranslator(source='auto', target='fr').translate(texte)
    except:
        return texte # En cas d'erreur, garde le texte original

# --- CONFIGURATION ---
TOKEN = "8547065074:AAEiZ4Jw5maZMbkYAIiJtnrIMPv1hk5dU54"

# Ta liste avec ton ID et celui de Léa
LISTE_ID = ["6773491313", "7776912126"]

SOURCES = {
    # --- FRANCE ---
    "3Dnatives (FR)": "https://www.3dnatives.com/feed/",
    "Cults3D (FR)": "https://cults3d.com/fr/flux-de-conception.rss",
    
    # --- CHINE & ASIE ---
    "Bambu Lab (Chine)": "https://blog.bambulab.com/feed/",
    "Creality (Chine)": "https://www.creality.com/blog/rss",
    "Seeed Studio (Hardware)": "https://www.seeedstudio.com/blog/feed/",
    
    # --- USA & INTERNATIONAL ---
    "3DPrint.com (USA)": "https://3dprint.com/feed/",
    "All3DP": "https://all3dp.com/feed/",
    "Printables (Prusa)": "https://blog.prusa3d.com/feed/",
    "Tom's Hardware (3D)": "https://www.tomshardware.com/rss/3d-printing",
    
    # --- PROTOTYPAGE & MAKER ---
    "Thingiverse": "https://www.thingiverse.com/rss/newest",
    "Instructables": "https://www.instructables.com/rss/workshop/",
    "Hackster.io": "https://www.hackster.io/feed",
    "Hackaday": "https://hackaday.com/blog/category/3d-printing/feed/",
    
    # --- RUSSIE ---
    "3DToday (Russie)": "https://3dtoday.ru/news/rss"
}

def envoyer_telegram(message):
    for chat_id in LISTE_ID:
        url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
        payload = {"chat_id": chat_id, "text": message, "parse_mode": "Markdown"}
        try:
            requests.post(url, data=payload)
        except Exception as e:
            print(f"Erreur d'envoi pour {chat_id}: {e}")

def compiler_actus_3d():
    message_global = "🌍 *ACTUS 3D & PROTOTYPAGE MONDIAL*\n\n"
    il_y_a_24h = datetime.now() - timedelta(hours=24)
    trouve = False

    for nom_site, url_rss in SOURCES.items():
        try:
            flux = feedparser.parse(url_rss)
            for article in flux.entries[:3]:
                date_tuple = article.published_parsed if hasattr(article, 'published_parsed') else article.updated_parsed
                if date_tuple:
                    date_article = datetime(*date_tuple[:6])
                    if date_article > il_y_a_24h:
                        trouve = True
                        message_global += f"📍 *{nom_site}*\n"
                        # ICI ON UTILISE LA TRADUCTION
                        message_global += f"👉 {traduire(article.title)}\n"
                        message_global += f"[Lire l'article]({article.link})\n\n"
        except:
            continue

    if trouve:
        envoyer_telegram(message_global)
    else:
        envoyer_telegram("☕ Rien de nouveau sur la planète 3D ce matin, David et Léa.")

if __name__ == "__main__":
    compiler_actus_3d()
