import os
import sys
import json
import requests
import feedparser
import schedule
import time
import google.generativeai as genai
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Optional
from dotenv import load_dotenv

# Import sécurisé
try:
    from video_animator import creer_video_article
except ImportError:
    print("⚠️ Module 'video_animator' introuvable. Vérifie le nom du fichier.")

load_dotenv()

# --- CONFIGURATION ---
TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "")
# On gère le cas où LISTE_ID est vide pour éviter les crashs
IDS_STR = os.getenv("TELEGRAM_CHAT_IDS", "")
LISTE_ID = [id.strip() for id in IDS_STR.split(",") if id.strip()]
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")

# Initialisation Gemini
if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)
    model = genai.GenerativeModel('gemini-1.5-flash')

# Dossiers
BASE_DIR = Path(__file__).parent
IMAGES_DIR = BASE_DIR / "images"
VIDEOS_DIR = BASE_DIR / "videos" # Ajout d'un dossier pour stocker les sorties
CACHE_FILE = BASE_DIR / "articles_cache.json"

for folder in [IMAGES_DIR, VIDEOS_DIR]:
    folder.mkdir(exist_ok=True)

# Sources
RSS_FEEDS = {
    "3dnatives": "https://www.3dnatives.com/fr/feed/",
    "fabbaloo": "https://www.fabbaloo.com/blog/feed.xml",
}

KEYWORDS = ["impression 3d", "3d printing", "additive manufacturing", "cao", "résine", "fdm", "prototypage"]

# --- LOGIQUE ---

def generer_script(titre: str, resume: str, source: str) -> str:
    prompt = f"Tu es Angie, présentatrice passionnée du JT 3D. Adapte cette info pour un script de 30s : {titre}. Résumé : {resume}. Source : {source}. Donne uniquement le texte."
    try:
        response = model.generate_content(prompt)
        return response.text.strip()
    except Exception as e:
        print(f"⚠️ Erreur Gemini : {e}")
        return f"L'actu du jour avec {source} : {titre}."

def scraper_rss() -> List[Dict]:
    articles = []
    for name, url in RSS_FEEDS.items():
        try:
            feed = feedparser.parse(url)
            for entry in feed.entries[:8]:
                txt = (entry.get('title', '') + " " + entry.get('summary', '')).lower()
                if any(kw in txt for kw in KEYWORDS):
                    articles.append({
                        "source": name,
                        "title": entry.get('title', 'Sans titre'),
                        "link": entry.get('link', ''),
                        "summary": entry.get('summary', '')[:300]
                    })
        except Exception as e:
            print(f"❌ Erreur {name}: {e}")
    return articles

def envoyer_telegram(video_path: str, article: Dict):
    message = (
        f"🎙 **FLASH INFO 3D**\n\n"
        f"📽 *{article['title']}*\n\n"
        f"🔗 [Lire l'article complet]({article['link']})\n"
        f"📡 Source : {article['source'].upper()}"
    )
    for chat_id in LISTE_ID:
        try:
            with open(video_path, 'rb') as v:
                url = f"https://api.telegram.org/bot{TOKEN}/sendVideo"
                requests.post(url, data={'chat_id': chat_id, 'caption': message, 'parse_mode': 'Markdown'}, files={'video': v}, timeout=150)
            print(f"✅ Envoyé à {chat_id}")
        except Exception as e:
            print(f"❌ Erreur envoi : {e}")

def traiter_articles():
    print(f"\n🚀 Lancement du JT - {datetime.now().strftime('%H:%M')}")
    cache = set(json.load(open(CACHE_FILE)) if CACHE_FILE.exists() else [])
    
    nouveaux = [a for a in scraper_rss() if a['link'] not in cache]
    print(f"📊 {len(nouveaux)} nouveaux articles trouvés.")

    for article in nouveaux[:3]: # On traite max 3 articles
        try:
            script = generer_script(article['title'], article['summary'], article['source'])
            article['script_jt'] = script
            
            # Ici on cherche l'image d'Angie
            angie_img = str(IMAGES_DIR / "angie_neutre.png")
            
            video = creer_video_article(article, angie_img)
            
            if video and os.path.exists(video):
                envoyer_telegram(video, article)
                cache.add(article['link'])
        except Exception as e:
            print(f"❌ Erreur sur l'article : {e}")

    with open(CACHE_FILE, 'w') as f:
        json.dump(list(cache), f)

def main():
    if len(sys.argv) > 1 and sys.argv[1] == "now":
        traiter_articles()
    elif len(sys.argv) > 1 and sys.argv[1] == "schedule":
        heure = sys.argv[2] if len(sys.argv) > 2 else "20:00"
        schedule.every().day.at(heure).do(traiter_articles)
        print(f"⏰ Automate activé pour {heure}")
        while True:
            schedule.run_pending()
            time.sleep(60)
    else:
        print("Usage: python main.py [now|schedule HH:MM]")

if __name__ == "__main__":
    main()
