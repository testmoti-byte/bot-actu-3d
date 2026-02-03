import requests
import feedparser
from datetime import datetime, timedelta
from deep_translator import GoogleTranslator

def traduire(texte):
    try:
        # Traduit n'importe quelle langue vers le Français
        return GoogleTranslator(source='auto', target='fr').translate(texte)
    except:
        return texte 

# --- CONFIGURATION ---
TOKEN = "8547065074:AAEiZ4Jw5maZMbkYAIiJtnrIMPv1hk5dU54"
LISTE_ID = ["6773491313", "7776912126"]

SOURCES = {
    # --- FRANCE ---
    "3Dnatives (FR)": "https://www.3dnatives.com/feed/",
    "Cults3D (FR)": "https://cults3d.com/fr/flux-de-conception.rss",
    "Heliox (YouTube FR)": "https://www.youtube.com/feeds/videos.xml?channel_id=UCidjtV8Lid-7unVogZunfBw",
    
    # --- CHINE & ASIE ---
    "Bambu Lab (Chine)": "https://blog.bambulab.com/feed/",
    "Creality (Chine)": "https://www.creality.com/blog/rss",
    "Seeed Studio (Hardware)": "https://www.seeedstudio.com/blog/feed/",
    
    # --- USA & INTERNATIONAL ---
    "3DPrint.com (USA)": "https://3dprint.com/feed/",
    "All3DP": "https://all3dp.com/feed/",
    "Printables (Prusa)": "https://blog.prusa3d.com/feed/",
    "Tom's Hardware (3D)": "https://www.tomshardware.com/rss/3d-printing",
    "Makers Muse (YouTube US)": "https://www.youtube.com/feeds/videos.xml?channel_id=UC_7aK9qzG95xeVXYY9Wf0fQ",
    "Uncle Jessy (YouTube US)": "https://www.youtube.com/feeds/videos.xml?channel_id=UC5Lbnd97xsY-W3Xy7nMFIDg",
    
    # --- PROTOTYPAGE & MAKER ---
    "Thingiverse": "https://www.thingiverse.com/rss/newest",
    "Instructables": "https://www.instructables.com/rss/workshop/",
    "Hackster.io": "https://www.hackster.io/feed",
    "Hackaday": "https://hackaday.com/blog/category/3d-printing/feed/",
    
    # --- RUSSIE ---
    "3DToday (Russie)": "https://3dtoday.ru/news/rss", # Ajout de la virgule ici
    "Pikabu 3D (YouTube RU)": "https://www.youtube.com/feeds/videos.xml?channel_id=UC6f-C7_m9Z8L_F_286GAt9Q",

    # --- LINKEDIN (Via RSS.app ou service similaire) ---
    "Bambu Lab (LinkedIn)": "https://rss.app/feeds/v1.1/VOTRE_ID_BAMBU_LINKEDIN.xml",
    "Creality (LinkedIn)": "https://rss.app/feeds/v1.1/VOTRE_ID_CREALITY_LINKEDIN.xml"
} # Suppression de l'accolade en trop qui était ici

def envoyer_telegram(message):
    for chat_id in LISTE_ID:
        url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
        payload = {"chat_id": chat_id, "text": message, "parse_mode": "Markdown", "disable_web_page_preview": False}
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
                # Amélioration de la détection de date pour YouTube
                date_tuple = None
                for attr in ['published_parsed', 'updated_parsed', 'created_parsed']:
                    if hasattr(article, attr) and getattr(article, attr) is not None:
                        date_tuple = getattr(article, attr)
                        break
                
                if date_tuple:
                    date_article = datetime(*date_tuple[:6])
                    if date_article > il_y_a_24h:
                        trouve = True
                        # Icône différente si c'est YouTube
                        prefixe = "📺" if "YouTube" in nom_site else "📍"
                        message_global += f"{prefixe} *{nom_site}*\n"
                        message_global += f"👉 {traduire(article.title)}\n"
                        message_global += f"[Voir le contenu]({article.link})\n\n"
        except Exception as e:
            print(f"Erreur sur {nom_site}: {e}")
            continue

    if trouve:
        envoyer_telegram(message_global)
    else:
        envoyer_telegram("☕ Rien de neuf aujourd'hui pour David et Léa.")

if __name__ == "__main__":
    compiler_actus_3d()

